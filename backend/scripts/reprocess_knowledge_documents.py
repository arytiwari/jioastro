"""
Re-process Knowledge Documents to Extract Rules
Runs all existing documents through the new GPT-4 rule extraction pipeline
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.supabase_service import supabase_service
from app.services.document_processor import document_processor


async def reprocess_all_documents():
    """Re-process all knowledge documents to extract rules"""

    print("🔄 Starting re-processing of knowledge documents...")
    print("=" * 70)

    try:
        # Get all knowledge documents
        print("📋 Fetching all knowledge documents...")
        response = supabase_service.client.table("knowledge_documents")\
            .select("*")\
            .execute()

        documents = response.data if response.data else []
        total_documents = len(documents)

        print(f"✅ Found {total_documents} documents to process")
        print()

        if total_documents == 0:
            print("ℹ️  No documents found to process")
            return

        # Statistics
        success_count = 0
        failed_count = 0
        rules_extracted_total = 0

        # Process each document
        for i, doc in enumerate(documents, 1):
            doc_id = doc.get('id')
            doc_title = doc.get('title', 'Unknown')
            doc_status = doc.get('is_indexed', 'unknown')

            print(f"\n[{i}/{total_documents}] Processing: {doc_title}")
            print(f"  Document ID: {doc_id}")
            print(f"  Current Status: {doc_status}")
            print("-" * 70)

            try:
                # Re-process the document
                result = await document_processor.process_document(doc_id)

                if result.get('success'):
                    success_count += 1
                    rules_extracted = result.get('stats', {}).get('rules_extracted', 0)
                    rules_extracted_total += rules_extracted

                    print(f"  ✅ SUCCESS - Extracted {rules_extracted} rules")
                else:
                    failed_count += 1
                    print(f"  ❌ FAILED - {result.get('error', 'Unknown error')}")

            except Exception as e:
                failed_count += 1
                print(f"  ❌ ERROR - {str(e)}")

            print("-" * 70)

            # Small delay between documents to avoid rate limits
            if i < total_documents:
                print("  ⏳ Waiting 2 seconds before next document...")
                await asyncio.sleep(2)

        # Final summary
        print("\n")
        print("=" * 70)
        print("📊 RE-PROCESSING COMPLETE")
        print("=" * 70)
        print(f"✅ Successful: {success_count}/{total_documents}")
        print(f"❌ Failed: {failed_count}/{total_documents}")
        print(f"📚 Total Rules Extracted: {rules_extracted_total}")
        print()

        # Show updated knowledge base stats
        print("🔍 Updated Knowledge Base Stats:")
        print("-" * 70)

        # Count total rules
        rules_response = supabase_service.client.table("knowledge_base")\
            .select("*", count="exact")\
            .execute()

        total_rules = rules_response.count if hasattr(rules_response, 'count') else len(rules_response.data or [])

        print(f"📚 Total Rules in Knowledge Base: {total_rules}")

        # Count rules by domain
        domains_response = supabase_service.client.table("knowledge_base")\
            .select("domain")\
            .execute()

        domain_counts = {}
        if domains_response.data:
            for rule in domains_response.data:
                domain = rule.get('domain', 'unknown')
                domain_counts[domain] = domain_counts.get(domain, 0) + 1

        print("\n📊 Rules by Domain:")
        for domain, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {domain}: {count} rules")

        print("\n✅ All documents have been re-processed!")
        print("🔗 View results at: /admin/dashboard/knowledge")

    except Exception as e:
        print(f"\n❌ Fatal error during re-processing: {str(e)}")
        import traceback
        traceback.print_exc()


async def reprocess_single_document(document_id: str):
    """Re-process a single document by ID"""

    print(f"🔄 Re-processing document: {document_id}")
    print("=" * 70)

    try:
        # Check if document exists
        doc_response = supabase_service.client.table("knowledge_documents")\
            .select("*")\
            .eq("id", document_id)\
            .single()\
            .execute()

        if not doc_response.data:
            print(f"❌ Document not found: {document_id}")
            return

        doc = doc_response.data
        print(f"📄 Document: {doc.get('title')}")
        print(f"   Status: {doc.get('is_indexed')}")
        print()

        # Re-process
        result = await document_processor.process_document(document_id)

        if result.get('success'):
            rules_extracted = result.get('stats', {}).get('rules_extracted', 0)
            print(f"\n✅ SUCCESS - Extracted {rules_extracted} rules")
        else:
            print(f"\n❌ FAILED - {result.get('error', 'Unknown error')}")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Main entry point"""

    print("\n")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║  Knowledge Document Re-Processing Tool                            ║")
    print("║  Extracts rules from existing documents using GPT-4                ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print()

    # Check command line arguments
    if len(sys.argv) > 1:
        document_id = sys.argv[1]
        await reprocess_single_document(document_id)
    else:
        await reprocess_all_documents()


if __name__ == "__main__":
    asyncio.run(main())
