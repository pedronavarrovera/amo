
# API backend using FastAPI that allows you to:
#
# Analyze a debt cycle and generate a condonation email (/analyze-cycle)
# 
# Encrypt and send the email via Postmark (/send-condonation-email)
#
# Apply the cycle settlement to reduce debts (/apply-cycle)
#
# This code integrates modules from this repository, including quantum encryption and email delivery. 

import os
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Dict, Optional
from adjacencymatrixinsights import (
    find_debt_cycle_shortest_back,
    generate_condonation_email,
    apply_cycle_settlement
)
from quantum import MLKEM_512, encrypt_message, decrypt_message
from communicationsviaemail import send_email_via_postmark_http

app = FastAPI(title="DebtCycleAnalyzer API")

class DebtRequest(BaseModel):
    matrix: List[List[int]]
    node_names: Dict[int, str]
    start_node: str
    second_node: str
    recipients: List[str] = []
    encrypt: Optional[bool] = True

@app.post("/analyze-cycle")
def analyze_cycle(req: DebtRequest):
    cycle = find_debt_cycle_shortest_back(req.matrix, req.node_names, req.start_node, req.second_node)
    if not cycle:
        raise HTTPException(status_code=400, detail="No valid debt cycle found.")

    # Compute minimum transfer
    name_to_index = {v: k for k, v in req.node_names.items()}
    min_transfer = min(
        req.matrix[name_to_index[cycle[i]]][name_to_index[cycle[i + 1]]]
        for i in range(len(cycle) - 1)
    )

    email_body = generate_condonation_email(cycle, min_transfer)

    return {
        "cycle": cycle,
        "min_transfer": min_transfer,
        "email_body": email_body
    }

@app.post("/send-condonation-email")
def send_condonation_email(req: DebtRequest):
    cycle = find_debt_cycle_shortest_back(req.matrix, req.node_names, req.start_node, req.second_node)
    if not cycle:
        raise HTTPException(status_code=400, detail="No valid debt cycle found.")

    name_to_index = {v: k for k, v in req.node_names.items()}
    min_transfer = min(
        req.matrix[name_to_index[cycle[i]]][name_to_index[cycle[i + 1]]]
        for i in range(len(cycle) - 1)
    )

    email_body = generate_condonation_email(cycle, min_transfer)

    # Optionally perform quantum encryption
    if req.encrypt:
        kem = MLKEM_512()
        public_key, secret_key = kem.keygen()
        ciphertext, shared_secret_sender = kem.encaps(public_key)
        encrypted_body = encrypt_message(email_body, shared_secret_sender)
    else:
        encrypted_body = email_body

    # Load Postmark configuration from environment
    postmark_token = os.environ.get("POSTMARK_TOKEN")
    message_stream = os.environ.get("MESSAGE_STREAM", "amoserver1messagestream")

    if not postmark_token:
        raise HTTPException(status_code=500, detail="Missing POSTMARK_TOKEN in environment variables.")

    # Generate recipient list
    recipients = req.recipients or [f"{name.lower()}@cybereu.eu" for name in cycle[:-1]]

    # Send email to all recipients
    for recipient in recipients:
        send_email_via_postmark_http(
            server_token=postmark_token,
            from_email="info@cybereu.eu",
            to_email=recipient,
            subject="Quantum-Safe Suggested Condonation",
            html_body=f"<pre>{encrypted_body}</pre>",
            message_stream=message_stream
        )

    return {
        "status": "success",
        "encrypted_body": encrypted_body,
        "cycle": cycle,
        "min_transfer": min_transfer,
        "recipients": recipients
    }

@app.post("/apply-cycle")
def apply_cycle(req: DebtRequest):
    cycle = find_debt_cycle_shortest_back(req.matrix, req.node_names, req.start_node, req.second_node)
    if not cycle:
        raise HTTPException(status_code=400, detail="No valid debt cycle found.")

    apply_cycle_settlement(req.matrix, req.node_names, cycle)
    return {
        "message": "Cycle settlement applied.",
        "updated_matrix": req.matrix
    }

# Docker support entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("debt_cycle_api:app", host="0.0.0.0", port=8000, reload=True)
