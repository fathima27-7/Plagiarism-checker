import io
import unittest
from app import create_app
from app.extensions import db
from app.models.document import Document
from app.models.analysis import AnalysisResult

class TestEndToEndWorkflow(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_complete_user_lifecycle(self):
        # 1. Prepare sample student paper (combining original text, citation, and copied sentence)
        sample_paper_content = (
            "Title: Modern Cloud Orchestration and Algorithmic Equity\n\n"
            "Abstract\n"
            "This study investigates microservices deployment and ethical AI algorithms.\n\n"
            "Introduction\n"
            "Cloud architectures rely heavily on container clusters. As noted in [1], zero-trust security provides continuous verification. "
            "In conclusion, it is important to note that machine learning plays a crucial role in modern society. "
            "Furthermore, artificial intelligence fosters a sense of technological advancement across multiple sectors.\n\n"
            "Methodology\n"
            "Machine learning systems are increasingly entrusted with high-stakes automated decisions, encompassing credit scoring, criminal recidivism prediction, employment screening, and medical diagnostics.\n\n"
            "Results and Discussion\n"
            "The experimental results were analyzed by our engineering team. Over 95% throughput was maintained.\n\n"
            "Conclusion\n"
            "Continuous verification and ethical constraints ensure robust academic and industry deployments.\n\n"
            "References\n"
            "[1] S. Rose et al., Zero Trust Architecture, NIST Special Publication 800-207, 2020."
        )

        # 2. Upload Document (Feature 1)
        data = {
            'file': (io.BytesIO(sample_paper_content.encode('utf-8')), 'student_submission.txt'),
            'is_reference': 'false'
        }
        res_upload = self.client.post('/api/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(res_upload.status_code, 201)
        upload_json = res_upload.get_json()
        doc_id = upload_json['document']['id']
        print(f"[E2E Step 1] Document uploaded successfully. ID: {doc_id}")

        # 3. Trigger Full Analytical Pipeline (Features 2, 3, 4, 5, 6, 8, 9, 10, 15)
        res_analyze = self.client.post('/api/analyze', json={'document_id': doc_id})
        self.assertEqual(res_analyze.status_code, 200)
        analyze_json = res_analyze.get_json()

        analysis_id = analyze_json['analysis_id']
        plag_score = analyze_json['analysis']['plagiarism_score']
        ai_score = analyze_json['analysis']['ai_likelihood_score']
        sections = analyze_json['sections']
        citations = analyze_json['citations']
        suggestions = analyze_json['suggestions']

        print(f"[E2E Step 2] Analysis completed. Analysis ID: {analysis_id}")
        print(f"            Plagiarism Similarity: {plag_score}%")
        print(f"            AI Likelihood Estimate: {ai_score}% (Risk: {analyze_json['analysis']['ai_risk_level']})")
        print(f"            Sections parsed: {len(sections)} (Titles: {[s['section_name'] for s in sections]})")
        print(f"            Citations checked: {len(citations)}")
        print(f"            Smart suggestions: {len(suggestions)}")

        self.assertGreater(len(sections), 0)
        self.assertGreaterEqual(len(citations), 1)

        # 4. Side-by-Side Comparison (Feature 7)
        with self.app.app_context():
            ref_doc = Document.query.filter_by(is_reference=True).first()
            ref_id = ref_doc.id

        res_compare = self.client.post('/api/compare', json={'doc1_id': doc_id, 'doc2_id': ref_id})
        self.assertEqual(res_compare.status_code, 200)
        compare_json = res_compare.get_json()
        print(f"[E2E Step 3] Side-by-Side Diff: Overall Similarity = {compare_json['overall_similarity']}%")

        # 5. Download ReportLab PDF (Feature 13)
        res_report = self.client.get(f'/reports/download/{analysis_id}')
        self.assertEqual(res_report.status_code, 200)
        self.assertEqual(res_report.headers['Content-Type'], 'application/pdf')
        print(f"[E2E Step 4] ReportLab PDF generated. Length: {len(res_report.data)} bytes")

        # 6. Check History (Feature 12)
        res_hist = self.client.get('/api/history')
        self.assertEqual(res_hist.status_code, 200)
        self.assertGreaterEqual(res_hist.get_json()['total'], 1)
        print(f"[E2E Step 5] History queried. Total records = {res_hist.get_json()['total']}")

        # 7. Document Privacy & Deletion (Feature 14)
        res_del = self.client.delete(f'/api/history/document/{doc_id}')
        self.assertEqual(res_del.status_code, 200)
        print(f"[E2E Step 6] Privacy hard purge executed: {res_del.get_json()['message']}")

        # Verify cascade deletion
        with self.app.app_context():
            deleted_doc = Document.query.get(doc_id)
            self.assertIsNone(deleted_doc)
            deleted_analysis = AnalysisResult.query.get(analysis_id)
            self.assertIsNone(deleted_analysis)
        print("[E2E Step 7] Cascade deletion verified. Clean state confirmed.")

if __name__ == '__main__':
    unittest.main()

