# from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
# from sqlalchemy.orm import Session
# from app.utils.ocr_utils import extract_text_from_eml_with_ocr
# from app.auth import get_current_user
# from app.database import get_db
# from app.models.user import User
# from app.models.products import ProductSKU
# from app.models.location import Country, State
# from app.schemas.order import OrderTextRequest
# from PyPDF2 import PdfReader
# from openai import OpenAI
# import pandas as pd
# import json
# import re
# import os
# import traceback
# import logging

# router = APIRouter(prefix="/chatgpt", tags=["ChatGPT Extract"])
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

# # ---------- Utility functions ----------

# def get_country_id_safe(location_db: Session, code_or_name: str) -> int | str:
#     if not code_or_name:
#         return ""
#     code_or_name = code_or_name.strip().upper()
#     country = location_db.query(Country).filter(
#         (Country.name.ilike(f"%{code_or_name}%")) |
#         (Country.two_letter_code == code_or_name) |
#         (Country.three_letter_code == code_or_name)
#     ).first()
#     return country.id if country else ""

# def get_state_id_safe(location_db: Session, code_or_name: str, country_id: int | str) -> int | str:
#     if not code_or_name or not country_id:
#         return ""
#     code_or_name = code_or_name.strip().upper()
#     state = location_db.query(State).filter(
#         State.country_id == country_id,
#         ((State.name.ilike(f"%{code_or_name}%")) | (State.code == code_or_name))
#     ).first()
#     return state.id if state else ""

# def resolve_sku_to_id_safe(product_db: Session, sku: str) -> int | str:
#     if not sku:
#         return ""
#     sku_obj = product_db.query(ProductSKU).filter(
#         ProductSKU.sku.ilike(sku.strip())
#     ).first()
#     return sku_obj.id if sku_obj else ""

# def transform_orders(
#     location_db: Session,
#     product_db: Session,
#     raw_orders: list[dict]
# ) -> list[dict]:
#     transformed_orders = []
#     for order in raw_orders:
#         country_input = order.get("recipientCountryCode")
#         state_input = order.get("recipientState")

#         country_id = int(country_input) if str(country_input).isdigit() else get_country_id_safe(location_db, str(country_input))
#         state_id = int(state_input) if str(state_input).isdigit() else get_state_id_safe(location_db, str(state_input), country_id)

#         items = []
#         for item in order.get("items", []):
#             sku = item.get("sku")
#             quantity = item.get("quantity", 1)
#             item_sku_id = resolve_sku_to_id_safe(product_db, sku)
#             items.append({
#                 "skuId": item_sku_id,
#                 "sku": sku,
#                 "quantity": quantity
#             })

#         transformed_orders.append({
#             "purchaseOrder": order.get("purchaseOrder"),
#             "purchaseDate": order.get("purchaseDate"),
#             "recipientFirstName": order.get("recipientFirstName"),
#             "recipientLastName": order.get("recipientLastName"),
#             "recipientAddress1": order.get("recipientAddress1"),
#             "recipientAddress2": order.get("recipientAddress2"),
#             "recipientCountryCode": country_id,
#             "recipientState": state_id,
#             "recipientZip": order.get("recipientZip"),
#             "recipientPhoneNumber": order.get("recipientPhoneNumber"),
#             "items": items
#         })

#     return transformed_orders

# def extract_json_from_gpt(raw_response: str):
#     try:
#         cleaned = re.sub(r"```(?:json)?", "", raw_response).strip("` \n")
#         json_start = cleaned.find("[")
#         json_end = cleaned.rfind("]") + 1
#         json_part = cleaned[json_start:json_end]
#         return json.loads(json_part)
#     except Exception as e:
#         print("GPT response malformed or not valid JSON:", raw_response)
#         raise e

# # ---------- Endpoints ----------

# @router.post("/extract-order")
# def extract_order_from_file(
#     file: UploadFile = File(...),
#     location_db: Session = Depends(get_db("drop_ship_seller")),
#     product_db: Session = Depends(get_db("products_db")),
#     current_user: User = Depends(get_current_user)
# ):
#     try:
#         extension = file.filename.split(".")[-1].lower()
#         content = ""

#         if extension == "pdf":
#             reader = PdfReader(file.file)
#             content = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
#         elif extension == "csv":
#             decoded = file.file.read().decode("utf-8")
#             content = decoded
#         elif extension in ["xlsx", "xls"]:
#             df = pd.read_excel(file.file)
#             content = df.to_csv(index=False)
#         elif extension == "eml":
#             content = extract_text_from_eml_with_ocr(file.file)
#         else:
#             raise HTTPException(status_code=400, detail="Unsupported file format")

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"File reading failed: {str(e)}")

#     # ChatGPT Prompt
#     system_prompt = (
#         "You are an API data extractor. Return a strict JSON array in the format below:\n"
#         "[{\n"
#         " \"purchaseOrder\": \"string\",\n"
#         " \"purchaseDate\": \"string\",\n"
#         " \"recipientFirstName\": \"string\",\n"
#         " \"recipientLastName\": \"string\",\n"
#         " \"recipientAddress1\": \"string\",\n"
#         " \"recipientAddress2\": \"string (optional, leave blank if not present)\",\n"
#         " \"recipientCountryCode\": string (like 'US'),\n"
#         " \"recipientState\": string (like 'TN'),\n"
#         " \"recipientZip\": \"string\",\n"
#         " \"recipientPhoneNumber\": \"string\",\n"
#         " \"items\": [{ \"sku\": string, \"quantity\": number }]\n"
#         "}]\n\n"
#         "**Instructions:**\n"
#         "- Extract address components properly. Do not place city/state/zip/country in `recipientAddress2`.\n"
#         "- Use only the street line as `recipientAddress1`. Leave `recipientAddress2` empty if not available.\n"
#         "- Respond ONLY with raw JSON, no markdown or explanation."
#     )

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4",
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": content}
#             ],
#             temperature=0
#         )

#         gpt_raw = response.choices[0].message.content
#         print("=== GPT RAW ===")
#         print(gpt_raw[:1000])
#         print("===============")

#         parsed = extract_json_from_gpt(gpt_raw)
#         transformed = transform_orders(location_db, product_db, parsed)
#         return {"orders": transformed}

#     except Exception as e:
#         print("ERROR GPT PARSE >>>", str(e))
#         traceback.print_exc()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="500: Failed to parse GPT response"
#         )

# @router.post("/extract-order-from-text")
# def extract_order_from_text(
#     payload: OrderTextRequest,
#     location_db: Session = Depends(get_db("drop_ship_seller")),
#     product_db: Session = Depends(get_db("products_db")),
#     current_user: User = Depends(get_current_user)
# ):
#     system_prompt = (
#         "You are an API data extractor. Return a strict JSON array in the format below:\n"
#         "[{\n"
#         " \"purchaseOrder\": \"string (or blank if not present)\",\n"
#         " \"purchaseDate\": \"string (or blank if not present)\",\n"
#         " \"recipientFirstName\": \"string (or blank)\",\n"
#         " \"recipientLastName\": \"string (or blank)\",\n"
#         " \"recipientAddress1\": \"string (or blank)\",\n"
#         " \"recipientAddress2\": \"string (optional, leave blank if not present)\",\n"
#         " \"recipientCountryCode\": string (like 'US', or blank),\n"
#         " \"recipientState\": string (like 'FL', or blank),\n"
#         " \"recipientZip\": \"string (or blank)\",\n"
#         " \"recipientPhoneNumber\": \"string (or blank)\",\n"
#         " \"items\": [\n"
#         "   { \"sku\": string, \"quantity\": number }\n"
#         " ]\n"
#         "}]\n\n"
#         "**Important Extraction Rules:**\n"
#         "- Do NOT use product codes as purchaseOrder.\n"
#         "- Words like '1 set' or '2 pieces' imply quantity.\n"
#         "- Only include product SKUs as items. Ignore unrelated words.\n"
#         "- Respond ONLY with raw JSON. No markdown. No explanation."
#     )

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4",
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": payload.text}
#             ],
#             temperature=0
#         )

#         gpt_raw = response.choices[0].message.content
#         print("=== GPT TEXT RAW ===")
#         print(gpt_raw[:1000])
#         print("====================")

#         parsed = extract_json_from_gpt(gpt_raw)
#         transformed = transform_orders(location_db, product_db, parsed)
#         return {"orders": transformed}

#     except Exception as e:
#         print("ERROR GPT TEXT PARSE >>>", str(e))
#         traceback.print_exc()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="500: Failed to parse GPT response"
#         )
