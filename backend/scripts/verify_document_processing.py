#!/usr/bin/env python3
"""
Verify that documents have been properly processed with rule extraction
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.supabase_service import supabase_service

def verify_processing():
    print("\n" + "="*80)
    print("📊 DOCUMENT PROCESSING VERIFICATION")
    print("="*80)

    # Get all documents
    docs_response = supabase_service.client.table("knowledge_documents").select("*").execute()
    documents = docs_response.data or []

    print(f"\n📄 Total documents: {len(documents)}")

    # Get all rules
    rules_response = supabase_service.client.table("knowledge_base").select("*").execute()
    rules = rules_response.data or []

    print(f"📚 Total rules: {len(rules)}")

    print("\n" + "-"*80)
    print("DOCUMENT ANALYSIS")
    print("-"*80)

    for doc in documents:
        print(f"\n📖 {doc['title']}")
        print(f"   Type: {doc['document_type']}")
        print(f"   Status: {doc['is_indexed']}")
        print(f"   File: {doc.get('original_filename', 'N/A')}")

        meta = doc.get('doc_metadata', {})
        text_length = meta.get('text_length', 0)
        num_chunks = meta.get('num_chunks', 0)
        num_embeddings = meta.get('num_embeddings', 0)

        print(f"   Text extracted: {text_length:,} characters")
        print(f"   Chunks: {num_chunks}")
        print(f"   Embeddings: {num_embeddings}")

        # Determine if processing was successful
        if text_length < 1000:
            print(f"   ⚠️  WARNING: Very little text extracted - likely scanned PDF!")
            print(f"   💡 Action: Re-upload with OCR'd PDF or text file")
        elif text_length < 10000:
            print(f"   ⚠️  WARNING: Less text than expected for a full book")
        else:
            print(f"   ✅ Good amount of text extracted")

        # Check for linked rules
        doc_rules = [r for r in rules if r.get('document_id') == doc['id']]
        print(f"   Rules extracted: {len(doc_rules)}")

        if len(doc_rules) == 0 and text_length > 1000:
            print(f"   ⚠️  WARNING: No rules extracted despite having text!")
            print(f"   💡 Action: May need to manually trigger rule extraction")
        elif len(doc_rules) > 0:
            print(f"   ✅ Rules successfully extracted")

    print("\n" + "-"*80)
    print("RULES ANALYSIS")
    print("-"*80)

    # Group rules by document_id
    rules_by_doc = {}
    orphan_rules = []

    for rule in rules:
        doc_id = rule.get('document_id')
        if doc_id:
            rules_by_doc[doc_id] = rules_by_doc.get(doc_id, 0) + 1
        else:
            orphan_rules.append(rule)

    print(f"\n📚 Rules linked to documents: {sum(rules_by_doc.values())}")
    print(f"📚 Rules not linked (sample/orphan): {len(orphan_rules)}")

    if orphan_rules:
        print(f"\n   Sample orphan rules:")
        for rule in orphan_rules[:3]:
            print(f"   - {rule.get('rule_id')}: {rule.get('anchor', 'N/A')[:60]}...")

    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)

    has_issues = False

    for doc in documents:
        meta = doc.get('doc_metadata', {})
        text_length = meta.get('text_length', 0)

        if text_length < 1000:
            has_issues = True
            print(f"\n⚠️  '{doc['title']}':")
            print(f"   - Only {text_length} characters extracted (likely scanned PDF)")
            print(f"   - Action: Re-upload with OCR or text version")
            print(f"   - Expected: 10,000+ characters for proper rule extraction")

    if not has_issues:
        print("\n✅ All documents appear to be processed correctly!")

    print("\n" + "="*80)

if __name__ == "__main__":
    verify_processing()
