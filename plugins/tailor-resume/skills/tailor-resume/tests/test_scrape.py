from tailor_resume.scrape import ScrapeResult, clean_html_text, save_scrape_artifacts


def test_clean_html_text_removes_scripts_and_collapses_whitespace():
    html = """
    <html><head><script>ignore()</script></head>
    <body><h1>Data Scientist</h1><p>Build models.</p><p>Use Python.</p></body></html>
    """

    text = clean_html_text(html)

    assert "ignore" not in text
    assert "Data Scientist" in text
    assert "Build models." in text
    assert "Use Python." in text


def test_save_scrape_artifacts_writes_raw_cleaned_and_metadata(tmp_path):
    result = ScrapeResult(
        url="https://example.com/job",
        status="success",
        raw_html="<html><body>Job</body></html>",
        cleaned_text="Job description",
        fallback_required=False,
        message="scraped with requests",
    )

    save_scrape_artifacts(result, tmp_path)

    assert (tmp_path / "job-raw.html").read_text(encoding="utf-8") == result.raw_html
    assert (tmp_path / "job.txt").read_text(encoding="utf-8") == "Job description"
    assert "fallback_required: false" in (tmp_path / "scrape.yaml").read_text(encoding="utf-8")
