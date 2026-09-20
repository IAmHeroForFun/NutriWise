from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Source
from .processors import pdf_processor, epub_processor, web_processor, food_extractor

@staff_member_required
def process_source(request, pk):
    source = get_object_or_404(Source, pk=pk)
    source.status = 'PROCESSING'
    source.error_message = ''
    source.save()

    try:
        pages = []
        if source.source_type == 'PDF':
            if not source.file:
                raise ValueError("PDF source has no attached file.")
            pages = pdf_processor.extract_pdf(source.file.path)
        elif source.source_type == 'EPUB':
            if not source.file:
                raise ValueError("EPUB source has no attached file.")
            pages = epub_processor.extract_epub(source.file.path)
        elif source.source_type == 'WEBSITE':
            if not source.url:
                raise ValueError("Website source has no URL provided.")
            pages = web_processor.scrape_website(source.url)
        else:
            raise ValueError(f"Unknown source type: {source.source_type}")

        if not pages:
            raise ValueError("No readable content could be extracted from this source.")

        count = food_extractor.extract_foods(pages, source)
        source.status = 'DONE'
        source.save()

        # Invalidate all cached daily plans so users immediately receive newly extracted foods
        from core.models import RecommendationResult
        RecommendationResult.objects.all().delete()

        messages.success(request, f"✓ Successfully extracted {count} food records from '{source.title}'. All daily plans refreshed!")
    except Exception as e:
        source.status = 'FAILED'
        source.error_message = str(e)
        source.save()
        messages.error(request, f"Processing failed for '{source.title}': {str(e)}")

    return redirect('/admin/documents/source/')
