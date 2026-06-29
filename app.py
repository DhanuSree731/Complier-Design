import re
import io
import json
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Any

import pandas as pd
import streamlit as st
import plotly.express as px

# =============================================================
# Compiler Visualization Tool
# =============================================================

st.set_page_config(
    page_title="Compiler Visualization Tool",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at top left, rgba(34, 211, 238, 0.18), transparent 28%),
        radial-gradient(circle at top right, rgba(168, 85, 247, 0.18), transparent 28%),
        linear-gradient(135deg, #030712 0%, #111827 45%, #1f2937 100%);
    color: #f8fafc;
}

[data-testid="stSidebar"] {
    background:
        linear-gradient(180deg, #020617 0%, #0f766e 45%, #581c87 100%);
    border-right: 1px solid rgba(255,255,255,0.12);
}

.main-title {
    text-align:center;
    font-size: 46px;
    font-weight: 900;
    background: linear-gradient(90deg, #22d3ee, #a78bfa, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 6px;
}

.sub-title {
    text-align:center;
    color: #d1d5db;
    font-size: 18px;
    margin-bottom: 24px;
    line-height: 1.6;
}

.card {
    background: rgba(17, 24, 39, 0.88);
    border: 1px solid rgba(34, 211, 238, 0.20);
    border-radius: 22px;
    padding: 24px;
    box-shadow: 0 18px 40px rgba(0,0,0,0.35);
    margin-bottom: 18px;
}

.glass-card {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px;
    padding: 18px;
    margin-bottom: 16px;
}

.metric-card {
    background: linear-gradient(135deg, #0891b2, #7c3aed);
    color: white;
    border-radius: 20px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 12px 28px rgba(14,165,233,0.22);
    min-height: 140px;
}

.metric-card h2 {margin: 0; font-size: 27px;}
.metric-card p {margin-top: 8px; opacity: 0.94; line-height: 1.45;}

.feature-card {
    background: linear-gradient(135deg, rgba(8,145,178,0.28), rgba(124,58,237,0.26));
    border: 1px solid rgba(255,255,255,0.14);
    color: #f8fafc;
    border-radius: 18px;
    padding: 18px;
    min-height: 150px;
}

.good-box {
    background: linear-gradient(135deg, #0f766e, #14b8a6);
    padding: 18px;
    border-radius: 15px;
    color: white;
    font-weight: 700;
}

.warn-box {
    background: linear-gradient(135deg, #b45309, #f97316);
    padding: 18px;
    border-radius: 15px;
    color: white;
    font-weight: 700;
}

.code-box {
    background: #020617;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 12px;
    color: #d1fae5;
    font-family: Consolas, monospace;
    white-space: pre-wrap;
}

.banner-img {
    text-align: center;
    margin: 14px auto 22px auto;
}

.banner-img img {
    border-radius: 18px;
    max-height: 140px;
    width: 42%;
    object-fit: cover;
    box-shadow: 0 12px 28px rgba(0,0,0,0.35);
    border: 1px solid rgba(255,255,255,0.18);
}

.banner-caption {
    color: #f8fafc;
    font-size: 14px;
    font-weight: 700;
    margin-top: 8px;
}

.small-note {
    color: #cbd5e1;
    font-size: 15px;
    line-height: 1.65;
}

.footer {
    text-align:center;
    color:#cbd5e1;
    padding:18px;
    border-top:1px solid rgba(148,163,184,0.18);
    margin-top:25px;
}


/* Better sidebar and page text visibility */
[data-testid="stSidebar"] * {
    color: #ffffff !important;
}
[data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
    color: #ffffff !important;
    font-weight: 700 !important;
}
.stMarkdown, .stText, p, li, label, span {
    color: #f8fafc;
}
h1, h2, h3, .stSubheader {
    color: #ffffff !important;
}

/* Medium readable Graphviz diagrams */
div[data-testid="stGraphVizChart"] {
    text-align: center !important;
    overflow-x: auto !important;
}
div[data-testid="stGraphVizChart"] svg {
    max-height: 620px !important;
    width: 92% !important;
    min-width: 680px !important;
    display: block !important;
    margin: 12px auto 26px auto !important;
}

/* Clear deployment/code text */
pre, code, .stCodeBlock, .stCodeBlock pre {
    background-color: #020617 !important;
    color: #ffffff !important;
    border: 1px solid #38bdf8 !important;
    border-radius: 14px !important;
    font-size: 18px !important;
    line-height: 1.8 !important;
    font-weight: 700 !important;
}
.stCodeBlock span, pre span, code span {
    color: #ffffff !important;
    font-weight: 700 !important;
}
div[data-testid="stMarkdownContainer"] code {
    color: #022c22 !important;
    background: #ccfbf1 !important;
    padding: 3px 7px !important;
    border-radius: 6px !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

PAGE_IMAGES = {
    "home": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?auto=format&fit=crop&w=1400&q=80",
    "pipeline": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=1400&q=80",
    "grammar": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1400&q=80",
    "deploy": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1400&q=80",
    "about": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1400&q=80",
}

def render_banner(image_key: str, caption: str):
    image_url = PAGE_IMAGES[image_key]
    html = f"""
    <div class="banner-img">
        <img src="{image_url}" alt="{caption}">
        <div class="banner-caption">{caption}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def compiler_insights(tokens_df: pd.DataFrame, code_text: str) -> pd.DataFrame:
    total_lines = len([line for line in code_text.splitlines() if line.strip()])
    unique_ids = tokens_df[tokens_df["type"] == "ID"]["value"].nunique() if not tokens_df.empty else 0
    operators = len(tokens_df[tokens_df["type"] == "OP"]) if not tokens_df.empty else 0
    return pd.DataFrame({
        "Metric": ["Non-empty lines", "Total tokens", "Unique identifiers", "Operators used"],
        "Value": [total_lines, len(tokens_df), unique_ids, operators]
    })


# ----------------------------- Lexer -----------------------------
TOKEN_SPEC = [
    ("NUMBER",   r"\d+(?:\.\d+)?"),
    ("KEYWORD",  r"\b(?:int|float|double|char|bool|if|else|while|return)\b"),
    ("ID",       r"[A-Za-z_]\w*"),
    ("OP",       r"==|!=|<=|>=|\+\+|--|&&|\|\||[+\-*/%=<>]"),
    ("LPAREN",   r"\("),
    ("RPAREN",   r"\)"),
    ("LBRACE",   r"\{"),
    ("RBRACE",   r"\}"),
    ("SEMI",     r";"),
    ("COMMA",    r","),
    ("SKIP",     r"[ \t]+"),
    ("NEWLINE",  r"\n"),
    ("MISMATCH", r"."),
]
TOKEN_REGEX = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)

@dataclass
class Token:
    type: str
    value: str
    line: int
    column: int


def lexical_analyze(code: str) -> Tuple[List[Token], List[str]]:
    tokens: List[Token] = []
    errors: List[str] = []
    line = 1
    line_start = 0
    for mo in re.finditer(TOKEN_REGEX, code):
        kind = mo.lastgroup or "MISMATCH"
        value = mo.group()
        column = mo.start() - line_start + 1
        if kind == "NUMBER":
            tokens.append(Token(kind, value, line, column))
        elif kind in {"KEYWORD", "ID", "OP", "LPAREN", "RPAREN", "LBRACE", "RBRACE", "SEMI", "COMMA"}:
            tokens.append(Token(kind, value, line, column))
        elif kind == "NEWLINE":
            line += 1
            line_start = mo.end()
        elif kind == "SKIP":
            continue
        elif kind == "MISMATCH":
            errors.append(f"Invalid character {value!r} at line {line}, column {column}")
    tokens.append(Token("EOF", "EOF", line, 1))
    return tokens, errors

# ----------------------------- Parser -----------------------------
@dataclass
class ASTNode:
    kind: str
    value: str = ""
    children: List[Any] = None
    def __post_init__(self):
        if self.children is None:
            self.children = []

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def current(self) -> Token:
        return self.tokens[self.pos]

    def match(self, token_type: str, value: Optional[str] = None) -> Token:
        tok = self.current()
        if tok.type == token_type and (value is None or tok.value == value):
            self.pos += 1
            return tok
        expected = value if value else token_type
        raise ParserError(f"Expected {expected}, got {tok.value} at line {tok.line}, column {tok.column}")

    def parse_program(self) -> ASTNode:
        stmts = []
        while self.current().type != "EOF":
            if self.current().type == "SEMI":
                self.match("SEMI")
                continue
            stmts.append(self.parse_statement())
        return ASTNode("Program", children=stmts)

    def parse_statement(self) -> ASTNode:
        tok = self.current()
        if tok.type == "KEYWORD" and tok.value in {"int", "float", "double", "char", "bool"}:
            return self.parse_declaration()
        if tok.type == "ID":
            return self.parse_assignment()
        if tok.type == "KEYWORD" and tok.value == "return":
            self.match("KEYWORD", "return")
            expr = self.parse_expression()
            self.match("SEMI")
            return ASTNode("Return", children=[expr])
        raise ParserError(f"Unsupported statement starts with {tok.value} at line {tok.line}")

    def parse_declaration(self) -> ASTNode:
        typ = self.match("KEYWORD").value
        name = self.match("ID").value
        children = []
        if self.current().type == "OP" and self.current().value == "=":
            self.match("OP", "=")
            children.append(self.parse_expression())
        self.match("SEMI")
        return ASTNode("Declaration", f"{typ} {name}", children)

    def parse_assignment(self) -> ASTNode:
        name = self.match("ID").value
        self.match("OP", "=")
        expr = self.parse_expression()
        self.match("SEMI")
        return ASTNode("Assignment", name, [expr])

    def parse_expression(self) -> ASTNode:
        return self.parse_additive()

    def parse_additive(self) -> ASTNode:
        node = self.parse_multiplicative()
        while self.current().type == "OP" and self.current().value in {"+", "-"}:
            op = self.match("OP").value
            right = self.parse_multiplicative()
            node = ASTNode("BinaryOp", op, [node, right])
        return node

    def parse_multiplicative(self) -> ASTNode:
        node = self.parse_factor()
        while self.current().type == "OP" and self.current().value in {"*", "/"}:
            op = self.match("OP").value
            right = self.parse_factor()
            node = ASTNode("BinaryOp", op, [node, right])
        return node

    def parse_factor(self) -> ASTNode:
        tok = self.current()
        if tok.type == "NUMBER":
            return ASTNode("Number", self.match("NUMBER").value)
        if tok.type == "ID":
            return ASTNode("Identifier", self.match("ID").value)
        if tok.type == "LPAREN":
            self.match("LPAREN")
            node = self.parse_expression()
            self.match("RPAREN")
            return node
        raise ParserError(f"Expected number, identifier, or '(' at line {tok.line}, column {tok.column}")

# ----------------------- Semantic + Symbol Table -----------------------
def build_symbol_table(ast: ASTNode) -> Tuple[pd.DataFrame, List[str]]:
    rows = []
    declared: Dict[str, Dict[str, str]] = {}
    errors = []

    def visit_expr(node: ASTNode):
        if node.kind == "Identifier" and node.value not in declared:
            errors.append(f"Semantic warning: variable '{node.value}' used before declaration")
        for child in node.children:
            visit_expr(child)

    for i, stmt in enumerate(ast.children, start=1):
        if stmt.kind == "Declaration":
            typ, name = stmt.value.split()
            if name in declared:
                errors.append(f"Semantic error: variable '{name}' redeclared")
            declared[name] = {"type": typ, "scope": "global", "line": str(i)}
            rows.append({"Name": name, "Type": typ, "Scope": "global", "Declared At Statement": i, "Initialized": "Yes" if stmt.children else "No"})
            for child in stmt.children:
                visit_expr(child)
        elif stmt.kind == "Assignment":
            if stmt.value not in declared:
                errors.append(f"Semantic warning: variable '{stmt.value}' assigned before declaration")
                rows.append({"Name": stmt.value, "Type": "unknown", "Scope": "global", "Declared At Statement": "-", "Initialized": "Yes"})
            visit_expr(stmt.children[0])
    return pd.DataFrame(rows), errors

# ----------------------------- TAC -----------------------------
class TACGenerator:
    def __init__(self):
        self.temp_count = 0
        self.code: List[Tuple[str, str, str, str]] = []

    def new_temp(self) -> str:
        self.temp_count += 1
        return f"t{self.temp_count}"

    def gen_expr(self, node: ASTNode) -> str:
        if node.kind == "Number":
            return node.value
        if node.kind == "Identifier":
            return node.value
        if node.kind == "BinaryOp":
            left = self.gen_expr(node.children[0])
            right = self.gen_expr(node.children[1])
            temp = self.new_temp()
            self.code.append((node.value, left, right, temp))
            return temp
        return "?"

    def generate(self, ast: ASTNode) -> pd.DataFrame:
        for stmt in ast.children:
            if stmt.kind == "Declaration" and stmt.children:
                name = stmt.value.split()[1]
                result = self.gen_expr(stmt.children[0])
                self.code.append(("=", result, "", name))
            elif stmt.kind == "Assignment":
                result = self.gen_expr(stmt.children[0])
                self.code.append(("=", result, "", stmt.value))
            elif stmt.kind == "Return":
                result = self.gen_expr(stmt.children[0])
                self.code.append(("return", result, "", ""))
        return pd.DataFrame(self.code, columns=["Op", "Arg1", "Arg2", "Result"])

# ----------------------------- Optimization -----------------------------
def is_num(x: str) -> bool:
    try:
        float(x)
        return True
    except Exception:
        return False


def optimize_tac(tac: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    optimized = []
    log = []
    constants: Dict[str, str] = {}

    for _, row in tac.iterrows():
        op, a1, a2, res = row["Op"], str(row["Arg1"]), str(row["Arg2"]), str(row["Result"])
        a1 = constants.get(a1, a1)
        a2 = constants.get(a2, a2)
        if op in {"+", "-", "*", "/"} and is_num(a1) and is_num(a2):
            val = eval(f"{float(a1)} {op} {float(a2)}")
            val = str(int(val)) if float(val).is_integer() else str(round(val, 4))
            constants[res] = val
            optimized.append(("=", val, "", res))
            log.append(f"Constant folding: {a1} {op} {a2} -> {val}")
        elif op == "=" and is_num(a1):
            constants[res] = a1
            optimized.append((op, a1, "", res))
            log.append(f"Constant propagation: {res} = {a1}")
        elif op == "*" and a2 == "1":
            optimized.append(("=", a1, "", res)); log.append(f"Algebraic simplification: {a1} * 1 -> {a1}")
        elif op == "+" and a2 == "0":
            optimized.append(("=", a1, "", res)); log.append(f"Algebraic simplification: {a1} + 0 -> {a1}")
        else:
            optimized.append((op, a1, a2, res))
    return pd.DataFrame(optimized, columns=["Op", "Arg1", "Arg2", "Result"]), log

# ----------------------------- Code Gen -----------------------------
def generate_assembly(tac: pd.DataFrame) -> str:
    lines = []
    for _, row in tac.iterrows():
        op, a1, a2, res = row["Op"], row["Arg1"], row["Arg2"], row["Result"]
        if op == "=":
            lines.append(f"MOV {res}, {a1}")
        elif op == "+":
            lines += [f"MOV R1, {a1}", f"ADD R1, {a2}", f"MOV {res}, R1"]
        elif op == "-":
            lines += [f"MOV R1, {a1}", f"SUB R1, {a2}", f"MOV {res}, R1"]
        elif op == "*":
            lines += [f"MOV R1, {a1}", f"MUL R1, {a2}", f"MOV {res}, R1"]
        elif op == "/":
            lines += [f"MOV R1, {a1}", f"DIV R1, {a2}", f"MOV {res}, R1"]
        elif op == "return":
            lines.append(f"RET {a1}")
    return "\n".join(lines)

# ----------------------------- Graphviz -----------------------------
def ast_to_dot(ast: ASTNode) -> str:
    lines = [
        "digraph AST {",
        'graph [rankdir=TB, ranksep=0.95, nodesep=0.55, bgcolor="transparent", size="10,7", ratio="compress"];',
        'node [shape=box, style="rounded,filled", fillcolor="#1e293b", color="#fbbf24", fontcolor="#ffffff", fontsize=18, penwidth=2.0, margin="0.20,0.14"];',
        'edge [color="#93c5fd", penwidth=1.8, arrowsize=0.8];'
    ]
    counter = 0
    def walk(node: ASTNode) -> int:
        nonlocal counter
        counter += 1
        node_id = counter
        label = f"{node.kind}\n{node.value}" if node.value else node.kind
        lines.append(f'n{node_id} [label="{label}"];')
        for child in node.children:
            child_id = walk(child)
            lines.append(f"n{node_id} -> n{child_id};")
        return node_id
    walk(ast)
    lines.append("}")
    return "\n".join(lines)


def cfg_to_dot(tac: pd.DataFrame) -> str:
    lines = [
        "digraph CFG {",
        'graph [rankdir=TB, ranksep=1.05, nodesep=0.75, bgcolor="transparent", size="8,9", ratio="compress"];',
        'node [shape=box, style="rounded,filled", fillcolor="#1e293b", color="#60a5fa", fontcolor="#ffffff", fontsize=18, width=2.8, height=0.85, penwidth=2.0, margin="0.20,0.14"];',
        'edge [color="#a7f3d0", penwidth=1.8, arrowsize=0.85];'
    ]
    for i, row in tac.iterrows():
        if row['Op'] == 'return':
            text = f"{i+1}: return {row['Arg1']}"
        elif row['Op'] == '=':
            text = f"{i+1}: {row['Result']} = {row['Arg1']}"
        else:
            text = f"{i+1}: {row['Result']} = {row['Arg1']} {row['Op']} {row['Arg2']}"
        lines.append(f'n{i} [label="{text}"];')
        if i < len(tac) - 1:
            lines.append(f"n{i} -> n{i+1};")
    lines.append("}")
    return "\n".join(lines)


def df_download(df: pd.DataFrame, filename: str, label: str):
    st.download_button(label, df.to_csv(index=False).encode("utf-8"), filename, "text/csv")


def full_report(tokens_df, symbols_df, tac_df, opt_df, opt_log, asm):
    report = {
        "tokens": tokens_df.to_dict(orient="records"),
        "symbol_table": symbols_df.to_dict(orient="records"),
        "intermediate_code": tac_df.to_dict(orient="records"),
        "optimized_code": opt_df.to_dict(orient="records"),
        "optimization_log": opt_log,
        "assembly": asm,
    }
    return json.dumps(report, indent=2)

# ----------------------------- UI -----------------------------
DEFAULT_CODE = """int a = 10;
int b = 20;
int c;
c = a + b * 2;
int d = (c + 0) * 1;
return d;
"""

st.sidebar.markdown("## 🧠 Compiler Studio")
page = st.sidebar.radio("Navigation", ["🏠 Home", "🔍 Compiler Pipeline", "📘 Grammar", "🚀 Deploy Guide", "ℹ️ About"])
st.sidebar.markdown("---")

if page == "🏠 Home":
    st.markdown('<div class="main-title">🧠 Compiler Phase Visualizer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">An interactive mini compiler that transforms source code into tokens, syntax structure, semantic data, intermediate code, optimized code, and assembly-style output.</div>', unsafe_allow_html=True)
    render_banner("home", "Compiler design dashboard with code analysis workflow")

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("Scanner", "Breaks source code into clean lexical tokens."),
        ("Parser", "Builds the syntax structure using grammar rules."),
        ("Analyzer", "Creates symbol table and semantic warnings."),
        ("Generator", "Produces TAC, optimized code, CFG and assembly.")
    ]
    for col, (h, p) in zip([c1, c2, c3, c4], cards):
        col.markdown(f'<div class="metric-card"><h2>{h}</h2><p>{p}</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🧩 Compiler Pipeline Roadmap")
    roadmap = pd.DataFrame({
        "Phase": ["Source Code", "Lexical Analysis", "Syntax Analysis", "Semantic Analysis", "Intermediate Code", "Optimization", "Target Code"],
        "Output": ["Mini C-like program", "Tokens", "AST / Parse Tree", "Symbol Table", "Three Address Code", "Optimized TAC", "Pseudo Assembly"]
    })
    st.dataframe(roadmap, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "🔍 Compiler Pipeline":
    st.markdown('<div class="main-title">🔍 Live Compiler Pipeline</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Write code, run the compiler, and watch every phase generate its own output.</div>', unsafe_allow_html=True)
    render_banner("pipeline", "Live compiler pipeline and source-code processing")
    code = st.text_area("Enter mini C-like code", DEFAULT_CODE, height=230)
    run = st.button("▶️ Compile and Visualize", use_container_width=True)

    if run:
        tokens, lex_errors = lexical_analyze(code)
        tokens_df = pd.DataFrame([t.__dict__ for t in tokens if t.type != "EOF"])
        st.subheader("1️⃣ Lexical Analysis")
        st.dataframe(tokens_df, use_container_width=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.write("Token distribution")
        if not tokens_df.empty:
            token_counts = tokens_df["type"].value_counts().reset_index()
            token_counts.columns = ["Token Type", "Count"]
            fig_tokens = px.pie(token_counts, names="Token Type", values="Count", title="Lexical Token Distribution")
            st.plotly_chart(fig_tokens, use_container_width=True)

            insight_df = compiler_insights(tokens_df, code)
            st.dataframe(insight_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if lex_errors:
            st.error("\n".join(lex_errors))
        df_download(tokens_df, "tokens.csv", "⬇️ Download Tokens CSV")

        try:
            parser = Parser(tokens)
            ast = parser.parse_program()
            symbols_df, semantic_errors = build_symbol_table(ast)
            tac_df = TACGenerator().generate(ast)
            opt_df, opt_log = optimize_tac(tac_df)
            asm = generate_assembly(opt_df)

            st.subheader("2️⃣ Parse Tree / AST")
            st.graphviz_chart(ast_to_dot(ast), use_container_width=True)

            st.subheader("3️⃣ Symbol Table")
            st.dataframe(symbols_df, use_container_width=True)
            if semantic_errors:
                st.warning("\n".join(semantic_errors))
            df_download(symbols_df, "symbol_table.csv", "⬇️ Download Symbol Table CSV")

            st.subheader("4️⃣ Intermediate Code: Three Address Code")
            st.dataframe(tac_df, use_container_width=True)
            df_download(tac_df, "intermediate_code.csv", "⬇️ Download TAC CSV")

            st.subheader("5️⃣ Optimization")
            left, right = st.columns(2)
            with left:
                st.write("Before Optimization")
                st.dataframe(tac_df, use_container_width=True)
            with right:
                st.write("After Optimization")
                st.dataframe(opt_df, use_container_width=True)
            if opt_log:
                st.markdown('<div class="good-box">Optimization Applied:<br>' + '<br>'.join(opt_log) + '</div>', unsafe_allow_html=True)
            else:
                st.info("No major optimization opportunities found.")
            df_download(opt_df, "optimized_code.csv", "⬇️ Download Optimized Code CSV")

            st.subheader("6️⃣ Control Flow Graph")
            st.graphviz_chart(cfg_to_dot(opt_df), use_container_width=True)

            st.subheader("7️⃣ Target Code / Assembly")
            st.code(asm, language="asm")

            st.subheader("8️⃣ Compiler Statistics")
            stats = pd.DataFrame({
                "Phase": ["Tokens", "Symbols", "TAC Lines", "Optimized Lines", "Optimizations"],
                "Count": [len(tokens_df), len(symbols_df), len(tac_df), len(opt_df), len(opt_log)]
            })
            fig = px.bar(stats, x="Phase", y="Count", title="Compiler Phase Output Counts", text="Count")
            st.plotly_chart(fig, use_container_width=True)

            report = full_report(tokens_df, symbols_df, tac_df, opt_df, opt_log, asm)
            st.download_button("⬇️ Download Full Compiler Report JSON", report.encode("utf-8"), "compiler_report.json", "application/json")
        except ParserError as e:
            st.error(f"Syntax Error: {e}")
        except Exception as e:
            st.error(f"Compiler Error: {e}")

elif page == "📘 Grammar":
    st.markdown('<div class="main-title">📘 Grammar Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">This grammar defines what type of mini C-like programs the compiler can understand.</div>', unsafe_allow_html=True)
    render_banner("grammar", "Grammar rules and parser structure")
    st.code("""
program     -> statement*
statement   -> declaration | assignment | return_statement
declaration -> type ID (= expression)? ;
assignment  -> ID = expression ;
return      -> return expression ;
expression  -> term ((+ | -) term)*
term        -> factor ((* | /) factor)*
factor      -> NUMBER | ID | ( expression )
type        -> int | float | double | char | bool
""", language="text")

elif page == "🚀 Deploy Guide":
    st.markdown('<div class="main-title">🚀 Deployment Guide</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Push the project to GitHub and deploy it on Streamlit Community Cloud.</div>', unsafe_allow_html=True)
    render_banner("deploy", "Cloud deployment and server workflow")
    st.markdown("### Local Run")
    st.code("""pip install -r requirements.txt
streamlit run app.py""", language=None)

    st.markdown("### GitHub Upload")
    st.code("""git init
git add .
git commit -m "Compiler visualization tool"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/compiler-visualization-tool.git
git push -u origin main""", language=None)

    st.markdown("### Streamlit Cloud")
    st.markdown("""
1. Open Streamlit Community Cloud.
2. Click **New app**.
3. Select your GitHub repository.
4. Main file path: `app.py`.
5. Deploy.

Keep `requirements.txt` in the same folder as `app.py` or in the repository root.
""")

else:
    st.markdown('<div class="main-title">ℹ️ About Project</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">A student-friendly advanced compiler design project with interactive visuals and downloadable reports.</div>', unsafe_allow_html=True)
    render_banner("about", "Compiler design, automation, and software engineering")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("This application explains compiler construction through live execution. Instead of only showing theory, it converts entered code into real compiler outputs step by step.")
    st.write("It is useful for mini projects, lab exams, GitHub portfolio, resume projects, and Streamlit deployment.")
    st.markdown('</div>', unsafe_allow_html=True)

    a, b, c = st.columns(3)
    a.markdown('<div class="feature-card"><h3>🎯 Purpose</h3><p>Understand compiler phases visually and practically.</p></div>', unsafe_allow_html=True)
    b.markdown('<div class="feature-card"><h3>🧪 Input</h3><p>Mini C-like declarations, assignments, expressions and returns.</p></div>', unsafe_allow_html=True)
    c.markdown('<div class="feature-card"><h3>📦 Output</h3><p>Tokens, AST, symbol table, TAC, optimized code and assembly.</p></div>', unsafe_allow_html=True)

st.markdown('<div class="footer">Compiler Visualization Tool</div>', unsafe_allow_html=True)