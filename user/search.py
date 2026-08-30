import json
import re
import requests

# AnythingLLM Endpoint Configuration
ANYTHING_LLM_URL = "http://localhost:3001/api/v1/workspace/search/chat"
ANYTHING_LLM_API_KEY = "3C196JT-8HA4GEC-M74S6W3-4SK5477"

def ask_ai_to_filter_names(user_prompt, candidate_names):
    """Sends the user prompt and database options to AnythingLLM.

    Strips the <think> process, normalizes formatting anomalies,
    and returns a clean Python list of names matching the candidate list
    using flexible cross-substring and case-insensitive validation.
    """
    if not user_prompt or not candidate_names:
        return []

    # 1. Dynamic Context Parsing (Handles both Strings and Rich Dicts safely)
    formatted_context = ""
    valid_lookup_names = []

    for item in candidate_names:
        if isinstance(item, dict):
            # Health-mode rich layout: Parse extensive clinical dictionary fields
            name_str = item.get("name", "").strip()
            type_str = item.get("type", "").strip()
            symptoms_str = item.get("symptoms", "").strip()
            info_str = item.get("info", "").strip()
            f2avoid_str = item.get("foods_to_avoid", "").strip()
            
            formatted_context += f"Disease Candidate: {name_str}\n"
            if type_str: formatted_context += f"Type/Category: {type_str}\n"
            if info_str: formatted_context += f"Description Info: {info_str}\n"
            if symptoms_str: formatted_context += f"Symptoms: {symptoms_str}\n"
            if f2avoid_str: formatted_context += f"Foods to Avoid: {f2avoid_str}\n"
            formatted_context += "\n"
            
            valid_lookup_names.append(name_str)
        else:
            # Food/General mode layout: Parse flat strings
            name_str = str(item).strip()
            formatted_context += f"Candidate Item: {name_str}\n\n"
            valid_lookup_names.append(name_str)

    # System instruction guiding the AI formatting
    system_instruction = (
        "CRITICAL: Ignore your workspace documents. Focus completely on the data provided below.\n"
        "You are a data filtering assistant. Analyze the USER_QUESTION and choose matches from SQL_PRE_FILTERED_LIST.\n"
        "Respond strictly by wrapping each exact matched name in brackets, like [b]item_Name[/b].\n"
        "use bold tags like [b]. "
    )

    ai_message = (
        f"{system_instruction}\n\n"
        f"USER_QUESTION: {user_prompt}\n\n"
        f"SQL_PRE_FILTERED_LIST:\n{formatted_context}"
    )

    payload = {
        "message": ai_message,
        "mode": "chat",  
        "stream": False
    }

    headers = {
        "Authorization": f"Bearer {ANYTHING_LLM_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # 🔥 FIXED: Explicitly targeting verified ANYTHING_LLM_URL destination string directly
        response = requests.post(ANYTHING_LLM_URL, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            resp_data = response.json()
            ai_text = resp_data.get("textResponse") or resp_data.get("content") or ""
            
            print("\n🔍 --- ANYTHINGLLM RAW RESPONSE START ---")
            print(ai_text)
            print("🔍 --- ANYTHINGLLM RAW RESPONSE END ---\n")
            
            if not ai_text.strip():
                return []

            # ✂️ CUT OUT THE THINK TAGS COMPLETELY
            if "</think>" in ai_text:
                final_output = ai_text.split("</think>")[-1].strip()
            else:
                final_output = ai_text.strip()

            print(f"📋 Post-Think Text before tag cleaning: '{final_output}'")

            # 🧽 STEP 1: CLEAN MALFORMED TAG ARTIFACTS
            final_output = re.sub(r'\[/?b\]', '', final_output, flags=re.IGNORECASE)  # Cleans [b] or [/b]
            final_output = final_output.replace('/b]', '').replace('[b', '')          # Cleans broken variants
            final_output = re.sub(r'<[^>]+>', '', final_output)                      # Strip any rogue HTML tags

            print(f"📋 Post-Think Text after tag cleaning: '{final_output}'")

            matched_results = []
            
            # 🎯 STEP 2: CASE-INSENSITIVE SMART BRACKET EXTRACTION
            bracket_matches = re.findall(r'\[([^\]]+)\]', final_output)
            
            for match in bracket_matches:
                clean_match = match.strip().lower()
                if not clean_match:
                    continue
                
                for candidate in valid_lookup_names:
                    candidate_clean = candidate.strip()
                    candidate_lower = candidate_clean.lower()
                    
                    # Match if exact, or if the bracket token is a core part of the database name
                    if (clean_match == candidate_lower or clean_match in candidate_lower or candidate_lower in clean_match):
                        if candidate_clean not in matched_results:
                            matched_results.append(candidate_clean)

            # 🔄 STEP 3: FLEXIBLE FALLBACK SUBSTRING MATCHING (If brackets failed or were dropped)
            if not matched_results:
                # Clean delimiters to isolate individual word boundaries
                normalized_search_space = final_output.replace('/', ' ').replace(',', ' ').replace('-', ' ').lower()
                
                for candidate in valid_lookup_names:
                    candidate_clean = candidate.strip()
                    candidate_lower = candidate_clean.lower().replace('-', ' ')
                    if not candidate_clean:
                        continue
                        
                    # Check substring intersections across both strings
                    if candidate_lower in normalized_search_space or normalized_search_space in candidate_lower:
                        if candidate_clean not in matched_results:
                            matched_results.append(candidate_clean)
                            
            # Last-resort word token comparison to absolutely guarantee no empty arrays on cross-matches
            if not matched_results:
                search_words = set(re.findall(r'\w+', final_output.lower()))
                for candidate in valid_lookup_names:
                    candidate_clean = candidate.strip()
                    candidate_words = set(re.findall(r'\w+', candidate_clean.lower()))
                    # If they share any significant identifying word (excluding short connecting tokens)
                    shared_words = search_words.intersection(candidate_words)
                    if any(len(word) > 2 for word in shared_words):
                        if candidate_clean not in matched_results:
                            matched_results.append(candidate_clean)

            print(f"🎯 Cleaned Python List Sent to views.py: {matched_results}")
            return matched_results
                
    except Exception as e:
        print(f"❌ Error during search.py clean text extraction: {e}")
        
    return []