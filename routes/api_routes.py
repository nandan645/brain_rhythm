from flask import request, jsonify, send_file, render_template
from extensions import db
from models import AccessRequest, DownloadToken
from utils.email import send_email, send_email_to_host
import uuid
import threading
from datetime import datetime, timedelta
from flask import send_file, current_app
import os



FILE_MAP = {
    1: "files/cerebellum/time_polycrystal.zip",
    2: "files/cerebellum/Structural_file.zip",
    3: "files/cerebellum/Resonance_map.zip",
    4: "files/cerebellum/Electric_field.zip",
    5: "files/cerebellum/Magnetic_field.zip",

    6: "files/hippocampus/time_polycrystal.zip",
    7: "files/hippocampus/Structural_file.zip",
    8: "files/hippocampus/Resonance_map.zip",
    9: "files/hippocampus/Electric_field.zip",
    10: "files/hippocampus/Magnetic_field.zip",

    11: "files/blood_vessel_network/time_polycrystal.zip",
    12: "files/blood_vessel_network/Structural_file.zip",
    13: "files/blood_vessel_network/Resonance_map.zip",
    14: "files/blood_vessel_network/Electric_field.zip",
    15: "files/blood_vessel_network/Magnetic_field.zip",

    16: "files/hypothalamus/time_polycrystal.zip",
    17: "files/hypothalamus/Structural_file.zip",
    18: "files/hypothalamus/Resonance_map.zip",
    19: "files/hypothalamus/Electric_field.zip",
    20: "files/hypothalamus/Magnetic_field.zip",

    21: "files/microtubule/time_polycrystal.zip",
    22: "files/microtubule/Structural_file.zip",
    23: "files/microtubule/Resonance_map.zip",
    24: "files/microtubule/Electric_field.zip",
    25: "files/microtubule/Magnetic_field.zip",

    26: "files/cranial_nerve/time_polycrystal.zip",
    27: "files/cranial_nerve/Structural_file.zip",
    28: "files/cranial_nerve/Resonance_map.zip",
    29: "files/cranial_nerve/Electric_field.zip",
    30: "files/cranial_nerve/Magnetic_field.zip",

    31: "files/thalamic_body/time_polycrystal.zip",
    32: "files/thalamic_body/Structural_file.zip",
    33: "files/thalamic_body/Resonance_map.zip",
    34: "files/thalamic_body/Electric_field.zip",
    35: "files/thalamic_body/Magnetic_field.zip",

    36: "files/thoracic_nerve/time_polycrystal.zip",
    37: "files/thoracic_nerve/Structural_file.zip",
    38: "files/thoracic_nerve/Resonance_map.zip",
    39: "files/thoracic_nerve/Electric_field.zip",
    40: "files/thoracic_nerve/Magnetic_field.zip",

    41: "files/cortical_branches/time_polycrystal.zip",
    42: "files/cortical_branches/Structural_file.zip",
    43: "files/cortical_branches/Resonance_map.zip",
    44: "files/cortical_branches/Electric_field.zip",
    45: "files/cortical_branches/Magnetic_field.zip",

    46: "files/neuron/time_polycrystal.zip",
    47: "files/neuron/Structural_file.zip",
    48: "files/neuron/Resonance_map.zip",
    49: "files/neuron/Electric_field.zip",
    50: "files/neuron/Magnetic_field.zip",

    51: "files/skin_nerve_net/time_polycrystal.zip",
    52: "files/skin_nerve_net/Structural_file.zip",
    53: "files/skin_nerve_net/Resonance_map.zip",
    54: "files/skin_nerve_net/Electric_field.zip",
    55: "files/skin_nerve_net/Magnetic_field.zip",

    56: "files/cortex_domain/time_polycrystal.zip",
    57: "files/cortex_domain/Structural_file.zip",
    58: "files/cortex_domain/Resonance_map.zip",
    59: "files/cortex_domain/Electric_field.zip",
    60: "files/cortex_domain/Magnetic_field.zip",

    61: "files/tubulin/time_polycrystal.zip",
    62: "files/tubulin/Structural_file.zip",
    63: "files/tubulin/Resonance_map.zip",
    64: "files/tubulin/Electric_field.zip",
    65: "files/tubulin/Magnetic_field.zip",
}


def register_api_routes(app):

    #Request Access
    @app.route("/api/request-access", methods=["POST"])
    def request_access():
        data = request.json
        email = data.get("email")
        file_id = data.get("file_id")

        if not email or not file_id:
            return jsonify({"error": "Email and file required"}), 400

        file_path = FILE_MAP.get(file_id)

        if not file_path:
            return jsonify({"error": "Invalid file"}), 400

        request_obj = AccessRequest(
            email=email,
            status="pending",
            file_path=file_path
        )
        db.session.add(request_obj)
        db.session.commit()
        base_url = current_app.config["BASE_URL"]
        approve_link = f"{base_url}/approve/{request_obj.id}"
        # approve_link = f"http://127.0.0.1:5000/approve/{request_obj.id}"

        app = current_app._get_current_object()

        def send_host_notification():
            with app.app_context():
                try:
                    send_email_to_host(email, approve_link, file_path)
                except Exception:
                    app.logger.exception("Failed to send download request email")

        threading.Thread(target=send_host_notification, daemon=True).start()

        return jsonify({
            "message": "Request submitted successfully. If approved, a time-limited download link will be emailed to you."
        })

    # Approve via Link
    @app.route('/approve/<int:req_id>')
    def approve_request(req_id):
        req = AccessRequest.query.get_or_404(req_id)

        file_name = req.file_path.split("/")[-1]
        file_name = file_name.replace("_", " ").title()

        if req.status != 'pending':
            return render_template(
                "approval_success.html",
                title="Request already handled",
                message="This approval link has already been used.",
                file_name=file_name,
                status_text=req.status.title(),
                show_email=False,
                email=req.email,
            ), 400

        req.status = 'approved'
        db.session.commit()

        token = str(uuid.uuid4())
        expiry = datetime.now() + timedelta(minutes=10)

        token_obj = DownloadToken(
            email=req.email,
            token=token,
            expires_at=expiry,
            file_path=req.file_path
        )
        db.session.add(token_obj)
        db.session.commit()
        base_url = current_app.config["BASE_URL"]
        download_link = f"{base_url}/download?token={token}"
        # download_link = f"http://127.0.0.1:5000/download?token={token}"

        send_email(req.email, "Your Download Link", f"""
    Your request has been approved.

    File: {file_name}

    Download:
    {download_link}

    Valid for 10 minutes (one-time use)
    """)

        return render_template(
            "approval_success.html",
            title="Approved",
            message=f"Download link sent to {req.email}.",
            email=req.email,
            file_name=file_name,
            status_text="Sent successfully",
            show_email=True,
        )



    # Download Endpoint
  

    @app.route("/download")
    def download():
        token = request.args.get("token")

        token_obj = DownloadToken.query.filter_by(token=token).first()

        if not token_obj:
            return "Invalid link", 404

        if token_obj.is_used:
            return "Link already used", 400

        if datetime.now() > token_obj.expires_at:
            return "Link expired", 400

        # CRITICAL FIX
        file_path = os.path.join(current_app.root_path, token_obj.file_path)

        if not os.path.exists(file_path):
            return f"File not found: {file_path}", 404

        token_obj.is_used = True
        db.session.commit()

        return send_file(file_path, as_attachment=True)