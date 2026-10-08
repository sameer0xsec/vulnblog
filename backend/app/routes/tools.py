from flask import Blueprint, request, jsonify
from ..auth_utils import require_auth, require_admin
from ..db import get_conn
import requests
import pickle
import base64
import subprocess
from lxml import etree

tools_bp = Blueprint("tools", __name__)

# VULN: SSRF — server fetches ANY attacker-supplied URL to build a "link
# preview", including internal network addresses (cloud metadata service,
# the db container on its internal hostname, etc.) and returns the body.
@tools_bp.route("/link-preview", methods=["POST"])
@require_auth
def link_preview():
    url = (request.json or {}).get("url", "")
    try:
        r = requests.get(url, timeout=3)
        return jsonify({"status": r.status_code, "preview": r.text[:500]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# VULN: insecure deserialization — drafts are saved as base64'd Python
# pickle blobs and unpickled on load with zero validation. A malicious
# pickle payload achieves remote code execution the moment it's loaded.
@tools_bp.route("/draft", methods=["POST"])
@require_auth
def save_draft():
    data = (request.json or {}).get("data", {})
    blob = base64.b64encode(pickle.dumps(data)).decode()
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO drafts (user_id, pickled_data) VALUES (%s,%s)", (request.user["id"], blob))
    conn.commit()
    draft_id = cur.lastrowid
    cur.close(); conn.close()
    return jsonify({"id": draft_id})

@tools_bp.route("/draft/<int:draft_id>")
@require_auth
def load_draft(draft_id):
    conn = get_conn(); cur = conn.cursor(dictionary=True)
    cur.execute(f"SELECT * FROM drafts WHERE id = {draft_id}")  # VULN: also SQL injection via path param reuse
    row = cur.fetchone()
    cur.close(); conn.close()
    if not row:
        return jsonify({"error": "Not found"}), 404
    data = pickle.loads(base64.b64decode(row["pickled_data"]))  # VULN: unpickling untrusted data = RCE
    return jsonify({"data": data})

# VULN: command injection — post id is interpolated straight into a shell
# command string passed to subprocess with shell=True.
@tools_bp.route("/export/<post_id>/pdf")
@require_auth
def export_pdf(post_id):
    cmd = f"echo Exporting post {post_id} && wkhtmltopdf-stub --post {post_id}"
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return jsonify({"output": out.decode(errors="replace")})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.output.decode(errors="replace"), "cmd": cmd}), 500  # VULN: echoes executed command

# VULN: XXE — lxml parser has entity resolution enabled (resolve_entities=True,
# no_network not restricting file:// access), so a crafted DOCTYPE with a
# SYSTEM entity can read local files.
@tools_bp.route("/import-xml", methods=["POST"])
@require_auth
@require_admin
def import_xml():
    xml_bytes = request.data
    parser = etree.XMLParser(resolve_entities=True, no_network=False)
    try:
        tree = etree.fromstring(xml_bytes, parser=parser)
        title = tree.findtext("title")
        return jsonify({"parsed_title": title})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
