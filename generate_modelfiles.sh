#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="./modelfiles"
TEMPLATE_SYSTEM='(IMPORT BASE SYSTEM PROMPT LOCATED @system/prompts/no-yap.txt EXACTLY)'

mkdir -p "$OUT_DIR"

create_file () {
    local filename="$1"
    local content="$2"

    if [[ -f "$filename" ]]; then
        echo "[SKIP] $filename already exists"
    else
        echo "[CREATE] $filename"
        printf "%s\n" "$content" > "$filename"
    fi
}

gen_modelfile () {
    local name="$1"
    local from="$2"
    local temp="$3"
    local top_p="$4"
    local repeat="$5"
    local ctx="$6"
    local predict="$7"

    local file="$OUT_DIR/Modelfile.${name}"

    create_file "$file" "FROM ${from}

PARAMETER temperature ${temp}
PARAMETER top_p ${top_p}
PARAMETER repeat_penalty ${repeat}
PARAMETER num_ctx ${ctx}
PARAMETER num_predict ${predict}

SYSTEM \"\"\"
${TEMPLATE_SYSTEM}
\"\"\""
}

### Planning
gen_modelfile "phi3-medium-planning" "phi3:medium" 0.3 0.9 1.15 4096 256
gen_modelfile "qwen2.5-7b-planning" "qwen2.5:7b" 0.25 0.9 1.1 4096 256
gen_modelfile "qwen2.5-3b-planning" "qwen2.5:3b" 0.3 0.92 1.2 3072 192
gen_modelfile "phi3-mini-planning" "phi3:mini" 0.35 0.92 1.2 3072 192

### Acting
gen_modelfile "codegemma-7b-acting" "codegemma:7b" 0.15 0.9 1.05 4096 512
gen_modelfile "codellama-7b-acting" "codellama:7b-instruct" 0.2 0.9 1.1 4096 512
gen_modelfile "qwen2.5-coder-7b-acting" "qwen2.5-coder:7b" 0.15 0.9 1.05 4096 512
gen_modelfile "qwen2.5-coder-3b-acting" "qwen2.5-coder:3b" 0.2 0.92 1.15 3072 384
gen_modelfile "codegemma-2b-acting" "codegemma:2b" 0.2 0.92 1.2 2048 256
gen_modelfile "starcoder2-7b-acting" "starcoder2:7b" 0.2 0.9 1.1 4096 512
gen_modelfile "starcoder2-3b-acting" "starcoder2:3b" 0.25 0.92 1.2 3072 384

echo "Done."
