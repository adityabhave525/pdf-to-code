import fitz  # PyMuPDF
import sys
import random
import textwrap
import re

# Fake enterprise words to generate realistic-sounding class/function names
PREFIXES =["Abstract", "Base", "Async", "Sync", "Dynamic", "Global", "Core", "Secure"]
NOUNS =["User", "Session", "Data", "Stream", "Auth", "Token", "Request", "Module", "Widget", "State"]
SUFFIXES =["Factory", "Manager", "Handler", "Service", "Controller", "Provider", "Resolver", "Middleware"]

def generate_fake_name():
    """Generates names like 'AbstractUserFactory' or 'AuthModuleHandler'"""
    return random.choice(PREFIXES) + random.choice(NOUNS) + random.choice(SUFFIXES)

def clean_and_chunk_text(doc):
    """Extracts text, fixes PDF line breaks, and groups into paragraphs."""
    full_text = ""
    for page in doc:
        full_text += page.get_text("text") + "\n\n"
    
    # Replace single newlines with spaces to fix broken PDF sentences, 
    # but keep double newlines for actual paragraph breaks.
    paragraphs = re.split(r'\n\s*\n', full_text)
    
    clean_paragraphs =[]
    for p in paragraphs:
        cleaned = p.replace("\n", " ").strip()
        if len(cleaned) > 20: # Ignore tiny random fragments or page numbers
            clean_paragraphs.append(cleaned)
            
    return clean_paragraphs

def template_jsdoc_class(text, name):
    wrapped_text = textwrap.indent(textwrap.fill(text, width=80), ' * ')
    return f"""
/**
{wrapped_text}
 */
export class {name} implements I{name} {{
    private readonly logger = new Logger({name}.name);
    
    constructor(private dependencies: InjectionToken) {{
        this.initializeState();
    }}

    private initializeState(): void {{
        // Setup internal context mapping
        this.logger.debug("Initializing context...");
    }}
}}
"""

def template_string_variable(text, name):
    # Escape backticks and template variables so it doesn't break TS
    safe_text = text.replace("`", "\\`").replace("${", "\\${")
    wrapped_text = textwrap.indent(textwrap.fill(safe_text, width=80), '        ')
    return f"""
export const validate{name} = async (payload: any): Promise<boolean> => {{
    const configurationDescription = `
{wrapped_text}
    `;
    
    return ConfigurationUtils.parseAndValidate(payload, configurationDescription);
}};
"""

def template_interface_docs(text, name):
    wrapped_text = textwrap.indent(textwrap.fill(text, width=80), ' * ')
    return f"""
/**
 * Interface definition for {name}.
{wrapped_text}
 */
export interface I{name} {{
    uuid: string;
    timestamp: number;
    metadata: Record<string, any>;
    status: 'ACTIVE' | 'PENDING' | 'RESOLVED';
}}
"""

def template_react_component(text, name):
    wrapped_text = textwrap.indent(textwrap.fill(text, width=80), '     * ')
    return f"""
export const {name}Component: React.FC<I{name}Props> = (props) => {{
    const [state, setState] = useState(null);

    /*
{wrapped_text}
     */
    useEffect(() => {{
        const subscription = ServiceBus.subscribe(props.id);
        return () => subscription.unsubscribe();
    }}, [props.id]);

    return <ErrorBoundary fallback={{<ErrorView />}}><WrappedView data={{state}} /></ErrorBoundary>;
}}
"""

def convert_to_stealth_code(pdf_path, output_path):
    print(f"🕵️  Extracting book from {pdf_path}...")
    doc = fitz.open(pdf_path)
    paragraphs = clean_and_chunk_text(doc)
    
    print(f"⚙️  Camouflaging {len(paragraphs)} paragraphs into enterprise code...")

    # Start with realistic-looking enterprise imports to sell the illusion
    ts_content = """import React, { useState, useEffect } from 'react';
import { Injectable, Logger } from '@nestjs/common';
import { Observable, BehaviorSubject } from 'rxjs';
import { ErrorBoundary } from './monitoring/ErrorBoundary';

// ============================================================================
// CORE SYSTEM MODULES
// Auto-generated bindings for strict type safety.
// ============================================================================

"""
    
    templates =[template_jsdoc_class, template_string_variable, template_interface_docs, template_react_component]

    # Interweave paragraphs into random code templates
    for para in paragraphs:
        # Prevent JSDoc escaping issues
        safe_para = para.replace("*/", "* /")
        
        template = random.choice(templates)
        fake_name = generate_fake_name()
        
        ts_content += template(safe_para, fake_name) + "\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ts_content)

    print(f"✅ Stealth file created: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf2stealth.py <input.pdf> [output.ts]")
        sys.exit(1)

    pdf_file = sys.argv[1]
    ts_file = sys.argv[2] if len(sys.argv) >= 3 else pdf_file.replace(".pdf", ".ts")
    
    convert_to_stealth_code(pdf_file, ts_file)