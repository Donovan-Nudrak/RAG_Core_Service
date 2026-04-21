#!/usr/bin/env bash

set -u

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
ROOT="${BASE_URL%/}"

SUCCESS_FILE="success.txt"
ERROR_FILE="errors.txt"

>"$SUCCESS_FILE"
>"$ERROR_FILE"

########################################
# Helpers
########################################

log_success() {
  echo "$1" >>"$SUCCESS_FILE"
}

log_error() {
  echo "$1" >>"$ERROR_FILE"
}

extract_json_field() {
  python3 -c "import json,sys; print(json.load(sys.stdin).get('$1',''))"
}

pretty_json() {
  python3 -c 'import json,sys; print(json.dumps(json.load(sys.stdin), indent=2, ensure_ascii=False))'
}

request() {
  # $1 = method
  # $2 = url
  # $3 = payload (optional)

  if [ -n "${3:-}" ]; then
    curl -s -w "\n%{http_code}" -X "$1" "$2" \
      -H "Content-Type: application/json" \
      -d "$3"
  else
    curl -s -w "\n%{http_code}" -X "$1" "$2"
  fi
}

split_response() {
  BODY=$(echo "$1" | head -n -1)
  STATUS=$(echo "$1" | tail -n1)
}

########################################
# 1. CREATE DOCUMENT (Hybrid test base)
########################################

DOC_TITLE="Hybrid Test Document"
DOC_CONTENT="Hybrid RAG test content. Unique token: HYBRID-TEST-XYZ-123"

payload_create=$(python3 -c "import json; print(json.dumps({'title':'$DOC_TITLE','content':'$DOC_CONTENT'}))")

RESP=$(request "POST" "$ROOT/documents" "$payload_create")
split_response "$RESP"

DOC_ID=$(echo "$BODY" | extract_json_field id)

if [ "$STATUS" -eq 200 ] && [ -n "$DOC_ID" ]; then
  log_success "Create document OK (id=$DOC_ID)"
else
  log_error "Create document FAILED (status=$STATUS)"
fi

########################################
# 2. REINDEX
########################################

RESP=$(request "POST" "$ROOT/documents/reindex")
split_response "$RESP"

if [ "$STATUS" -eq 200 ]; then
  log_success "Reindex OK"
else
  log_error "Reindex FAILED (status=$STATUS)"
fi

########################################
# 3. ASK (Hybrid validation)
########################################

ASK_Q="What unique token exists in the hybrid test content?"
payload_ask=$(python3 -c "import json; print(json.dumps({'question':'$ASK_Q'}))")

RESP=$(request "POST" "$ROOT/ask" "$payload_ask")
split_response "$RESP"

if [ "$STATUS" -eq 200 ] && echo "$BODY" | grep -q "HYBRID-TEST-XYZ-123"; then
  log_success "Ask (hybrid retrieval) OK"
else
  log_error "Ask (hybrid retrieval) FAILED"
fi

########################################
# 4. MULTI-QUESTION RAG TEST (file1 improved)
########################################

questions=(
  "What is artificial intelligence?"
  "Summarize available documents."
  "Difference between machine learning and deep learning?"
  "What is an embedding?"
  "What data exists in the knowledge base?"
  "How does a RAG system work?"
  "List main topics from context."
  "Is there something you cannot answer?"
)

i=1
for q in "${questions[@]}"; do
  payload=$(python3 -c "import json; print(json.dumps({'question': '$q'}))")

  RESP=$(request "POST" "$ROOT/ask" "$payload")
  split_response "$RESP"

  if [ "$STATUS" -eq 200 ] && echo "$BODY" | grep -q "answer"; then
    log_success "Ask batch [$i] OK"
  else
    log_error "Ask batch [$i] FAILED"
  fi

  i=$((i + 1))
done

########################################
# 5. NEGATIVE TESTS
########################################

# Empty document (should fail)
payload_bad='{"title":"Bad","content":"   "}'
RESP=$(request "POST" "$ROOT/documents" "$payload_bad")
split_response "$RESP"

if [ "$STATUS" -eq 400 ]; then
  log_success "Reject empty document OK"
else
  log_error "Reject empty document FAILED (status=$STATUS)"
fi

# Non-existent document
RESP=$(request "GET" "$ROOT/documents/999999")
split_response "$RESP"

if [ "$STATUS" -eq 404 ]; then
  log_success "Non-existent document OK"
else
  log_error "Non-existent document FAILED"
fi

########################################
# 6. DELETE + VALIDATION
########################################

RESP=$(request "DELETE" "$ROOT/documents/$DOC_ID")
split_response "$RESP"

if [ "$STATUS" -eq 200 ]; then
  log_success "Delete document OK"
else
  log_error "Delete document FAILED"
fi

RESP=$(request "GET" "$ROOT/documents")
split_response "$RESP"

if echo "$BODY" | grep -q "$DOC_ID"; then
  log_error "Deleted document still listed"
else
  log_success "Deleted document hidden OK"
fi

########################################
# SUMMARY
########################################

echo "Tests completed."
echo "-------------------------"
echo "Success log: $SUCCESS_FILE"
echo "Error log:   $ERROR_FILE"

SUCCESS_COUNT=$(wc -l <"$SUCCESS_FILE")
ERROR_COUNT=$(wc -l <"$ERROR_FILE")

echo ""
echo "Summary:"
echo "Success: $SUCCESS_COUNT"
echo "Errors:  $ERROR_COUNT"

if [ "$ERROR_COUNT" -gt 0 ]; then
  exit 1
else
  exit 0
fi
