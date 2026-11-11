import io
import unittest
from app import create_app
from app.models.document import Document
from app.models.analysis import AnalysisResult

class TestE2EWorkflow(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def test_complete_user_lifecycle(self):
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

        data = {
            'file': (io.BytesIO(sample_paper_content.encode('utf-8')), 'e2e_student_test.txt'),
            'is_reference': 'false'
        }
        res_upload = self.client.post('/api/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(res_upload.status_code, 201)
        doc_id = res_upload.get_json()['document']['id']

        res_analyze = self.client.post('/api/analyze', json={'document_id': doc_id})
        self.assertEqual(res_analyze.status_code, 200)
        analyze_json = res_analyze.get_json()
        analysis_id = analyze_json['analysis_id']

        self.assertGreater(analyze_json['analysis']['plagiarism_score'], 0)
        self.assertGreater(len(analyze_json['sections']), 0)
        self.assertGreater(len(analyze_json['citations']), 0)

        res_report = self.client.get(f'/reports/download/{analysis_id}')
        self.assertEqual(res_report.status_code, 200)
        self.assertEqual(res_report.headers['Content-Type'], 'application/pdf')

        res_del = self.client.delete(f'/api/history/document/{doc_id}')
        self.assertEqual(res_del.status_code, 200)

if __name__ == '__main__':
    unittest.main()

