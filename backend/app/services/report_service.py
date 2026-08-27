from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from jinja2 import Template
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class ReportService:
    @staticmethod
    def generate_html_report(
        dataset_info: Dict[str, Any],
        profile: Dict[str, Any],
        insights: Dict[str, Any],
        estimation_data: Optional[Dict[str, Any]],
        output_path: Path
    ) -> str:
        """Generates an HTML survey release report."""
        template_str = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>MoSPI Survey Analytical Release: {{ dataset.filename }}</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; color: #1e293b; background: #f8fafc; }
                .container { max-width: 900px; margin: 0 auto; background: white; padding: 32px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
                h1 { color: #0f172a; border-bottom: 2px solid #0284c7; padding-bottom: 12px; margin-bottom: 8px; }
                .badge { background: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 9999px; font-weight: 600; font-size: 0.875rem; }
                .card { background: #f1f5f9; padding: 18px; border-radius: 8px; margin: 20px 0; }
                table { width: 100%; border-collapse: collapse; margin-top: 14px; }
                th, td { padding: 10px 12px; border: 1px solid #cbd5e1; text-align: left; }
                th { background: #e2e8f0; font-weight: 600; }
                ul { padding-left: 20px; }
                li { margin-bottom: 6px; }
            </style>
        </head>
        <body>
            <div class="container">
                <span class="badge">Official MoSPI Statistical Release</span>
                <h1>Survey Processing & Estimation Report</h1>
                <p><strong>Dataset Source:</strong> {{ dataset.filename }} | <strong>Generated:</strong> {{ timestamp }}</p>
                
                <div class="card">
                    <h3>Executive Summary</h3>
                    <p>{{ insights.executive_summary }}</p>
                </div>

                <h3>Dataset Metrics</h3>
                <table>
                    <tr><th>Total Records</th><td>{{ profile.total_rows }}</td></tr>
                    <tr><th>Attributes</th><td>{{ profile.total_columns }}</td></tr>
                    <tr><th>Data Quality Score</th><td>{{ profile.quality_score.overall_score }}/100</td></tr>
                </table>

                {% if estimation %}
                <h3>Survey Parameter Estimation ({{ estimation.target_variable }})</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Estimation Mode</th>
                            <th>Point Estimate</th>
                            <th>Std. Error</th>
                            <th>Margin of Error</th>
                            <th>95% Confidence Interval</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Unweighted Sample</td>
                            <td>{{ estimation.unweighted.point_estimate }}</td>
                            <td>{{ estimation.unweighted.standard_error }}</td>
                            <td>±{{ estimation.unweighted.margin_of_error }}</td>
                            <td>[{{ estimation.unweighted.confidence_interval[0] }}, {{ estimation.unweighted.confidence_interval[1] }}]</td>
                        </tr>
                        {% if estimation.weighted %}
                        <tr style="background-color: #f0fdf4;">
                            <td><strong>Weighted Population</strong></td>
                            <td><strong>{{ estimation.weighted.point_estimate }}</strong></td>
                            <td>{{ estimation.weighted.standard_error }}</td>
                            <td>±{{ estimation.weighted.margin_of_error }}</td>
                            <td>[{{ estimation.weighted.confidence_interval[0] }}, {{ estimation.weighted.confidence_interval[1] }}]</td>
                        </tr>
                        {% endif %}
                    </tbody>
                </table>
                {% endif %}

                <h3>Data Quality & Consistency Findings</h3>
                <ul>
                    {% for item in insights.data_quality_findings %}
                    <li>{{ item }}</li>
                    {% endfor %}
                </ul>

                <h3>Methodological Recommendations</h3>
                <ul>
                    {% for rec in insights.recommendations %}
                    <li>{{ rec }}</li>
                    {% endfor %}
                </ul>
            </div>
        </body>
        </html>
        """
        template = Template(template_str)
        rendered = template.render(
            dataset=dataset_info,
            profile=profile,
            insights=insights,
            estimation=estimation_data,
            timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        )
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered)
        return str(output_path)

    @staticmethod
    def generate_pdf_report(
        dataset_info: Dict[str, Any],
        profile: Dict[str, Any],
        insights: Dict[str, Any],
        estimation_data: Optional[Dict[str, Any]],
        output_path: Path
    ) -> str:
        """Generates a publication-grade PDF report using ReportLab."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        elements = []

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=10
        )

        elements.append(Paragraph("MoSPI Survey Analytical & Estimation Report", title_style))
        elements.append(Paragraph(f"<b>File:</b> {dataset_info.get('filename')} | <b>Date:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles['Normal']))
        elements.append(Spacer(1, 14))

        # Quality Summary Table
        q_score = profile.get("quality_score", {}).get("overall_score", 0.0)
        summary_data = [
            ["Metric", "Value"],
            ["Total Survey Records", str(profile.get("total_rows", 0))],
            ["Total Attributes", str(profile.get("total_columns", 0))],
            ["Data Quality Index", f"{q_score}/100"]
        ]
        t = Table(summary_data, colWidths=[200, 300])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 16))

        # Executive Summary
        elements.append(Paragraph("<b>Executive Summary:</b>", styles['Heading3']))
        elements.append(Paragraph(insights.get("executive_summary", ""), styles['Normal']))
        elements.append(Spacer(1, 14))

        # Statistical Findings Table if available
        if estimation_data and "unweighted" in estimation_data:
            elements.append(Paragraph(f"<b>Estimation Summary ({estimation_data.get('target_variable')}):</b>", styles['Heading3']))
            unw = estimation_data.get("unweighted", {})
            w = estimation_data.get("weighted") or {}
            
            est_table = [
                ["Mode", "Estimate", "Std Error", "Margin of Error"],
                ["Unweighted", str(unw.get("point_estimate")), str(unw.get("standard_error")), f"±{unw.get('margin_of_error')}"],
                ["Weighted", str(w.get("point_estimate", "N/A")), str(w.get("standard_error", "N/A")), f"±{w.get('margin_of_error', 'N/A')}"]
            ]
            t_est = Table(est_table, colWidths=[120, 120, 120, 140])
            t_est.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0284c7")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(t_est)
            elements.append(Spacer(1, 14))

        doc.build(elements)
        return str(output_path)