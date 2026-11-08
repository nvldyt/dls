import json
from datetime import date, datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Hệ thống Quản trị Tổ Dược Lâm Sàng 20 Thành Viên",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================
# 1. DANH MỤC KHOA LÂM SÀNG, TÍNH CÁCH & NĂNG LỰC MẪU
# ==========================================
CLINICAL_DEPARTMENTS = [
    "Ban Giám đốc & Phòng KHTH (Điều phối chung)",
    "Khoa Khám bệnh & Điều trị Ngoại trú",
    "Khoa Hồi sức tích cực - Chống độc (ICU)",
    "Khoa Nội Tim mạch - Lão học",
    "Khoa Nội tiết - Đái tháo đường",
    "Khoa Bệnh nhiệt đới & Truyền nhiễm",
    "Khoa Thận - Tiết niệu & Lọc máu",
    "Khoa Nội Hô hấp - Tiêu hóa",
    "Khoa Sản - Phụ khoa",
    "Khoa Nhi tổng hợp",
    "Khoa Ung bướu & Huyết học lâm sàng",
    "Khoa Phẫu thuật - Gây mê hồi sức",
    "Khoa Ngoại Tổng hợp & Chấn thương",
    "Khoa Thần kinh - Cơ xương khớp",
    "Đơn vị Quản lý Đau & Chăm sóc giảm nhẹ",
    "Trung tâm Thông tin thuốc & Cảnh giác Dược (DI & ADR)",
    "Phòng Bảo hiểm Y tế & Kinh tế Dược",
    "Trung tâm Đào tạo & Nghiên cứu Khoa học",
]

SUBSYSTEMS = [
    "Phân hệ 1: Ban Điều phối & Quản trị Hệ thống",
    "Phân hệ 2: An toàn Đơn thuốc & Dược lý Cơ bản",
    "Phân hệ 3: Dược lâm sàng Chuyên khoa (Deep-Clinical)",
    "Phân hệ 4: Cảnh giác Dược, Thông tin Thuốc & Y tế Số",
    "Phân hệ 5: Kinh tế Dược & Đào tạo/Nghiên cứu",
]

WORKFLOW_STEPS = [
    "Bước 1: Tiếp nhận & Phân tích ban đầu (#01, #03)",
    "Bước 2: Rà soát An toàn & Chuyên khoa song song (#04-#12)",
    "Bước 3: Tổng hợp & Kiểm duyệt Quy chuẩn (#01, #02, #17, #18)",
    "Bước 4: Thẩm định chuyên môn bởi Dược sĩ (HITL)",
    "Bước 5: Truyền thông, Đào tạo & Theo dõi hậu lâm sàng (#13-#16, #19-#20)",
]


def get_default_members():
    return [
        {
            "id": "#01",
            "name": "DSCKII. Nguyễn Minh Quân",
            "code_role": "Chief Orchestrator (Tổng Điều phối DLS)",
            "subsystem": SUBSYSTEMS[0],
            "department": "Ban Giám đốc & Phòng KHTH (Điều phối chung)",
            "personality": "Quyết đoán, tư duy hệ thống, điềm tĩnh, giao tiếp đa chuyên khoa sắc bén",
            "competencies": "Điều phối luồng EMR/HIS, phân rã tác vụ hội chẩn toàn viện, tổng hợp phiếu tư vấn DLS",
            "skill_score": 96,
            "phase": "Giai đoạn 1 (Cốt lõi)",
            "tasks_assigned": 120,
            "tasks_completed": 115,
            "acceptance_rate": 96.5,
            "sla_compliance": 98.0,
            "adr_or_initiatives": 8,
        },
        {
            "id": "#02",
            "name": "ThS.DS. Trần Thu Hà",
            "code_role": "Clinical Compliance & Ethics (Kiểm duyệt Pháp lý Dược)",
            "subsystem": SUBSYSTEMS[0],
            "department": "Ban Giám đốc & Phòng KHTH (Điều phối chung)",
            "personality": "Nguyên tắc, cẩn trọng, tỉ mỉ, thượng tôn pháp luật và đạo đức y khoa",
            "competencies": "Kiểm soát quy chuẩn Nghị định 131/2020/NĐ-CP, thẩm định pháp lý khuyến nghị, bảo mật EMR",
            "skill_score": 94,
            "phase": "Giai đoạn 2 (Mở rộng)",
            "tasks_assigned": 110,
            "tasks_completed": 106,
            "acceptance_rate": 98.0,
            "sla_compliance": 97.0,
            "adr_or_initiatives": 6,
        },
        {
            "id": "#03",
            "name": "DSCKI. Lê Hoàng Nam",
            "code_role": "Medication History & Reconciliation (Đối soát Tiền sử Thuốc)",
            "subsystem": SUBSYSTEMS[1],
            "department": "Khoa Khám bệnh & Điều trị Ngoại trú",
            "personality": "Kiên nhẫn, quan sát tinh tế, giao tiếp thân thiện khi khai thác tiền sử người bệnh",
            "competencies": "Đối soát thuốc (MedRec) khi nhập/chuyển viện, phát hiện trùng lặp hoạt chất, OCR đơn thuốc",
            "skill_score": 90,
            "phase": "Giai đoạn 2 (Mở rộng)",
            "tasks_assigned": 150,
            "tasks_completed": 141,
            "acceptance_rate": 92.0,
            "sla_compliance": 95.0,
            "adr_or_initiatives": 5,
        },
        {
            "id": "#04",
            "name": "ThS.DS. Phạm Ngọc Ánh",
            "code_role": "Drug-Drug & Drug-Food Interaction (Rà soát Tương tác Thuốc)",
            "subsystem": SUBSYSTEMS[1],
            "department": "Khoa Nội Hô hấp - Tiêu hóa",
            "personality": "Nhạy bén, tư duy phân tích logic, phản ứng nhanh với các cảnh báo đỏ",
            "competencies": "Phân tích tương tác thuốc-thuốc & thuốc-thức ăn, phân tầng mức độ chống chỉ định, cảnh báo dị ứng",
            "skill_score": 93,
            "phase": "Giai đoạn 1 (Cốt lõi)",
            "tasks_assigned": 180,
            "tasks_completed": 174,
            "acceptance_rate": 94.5,
            "sla_compliance": 96.5,
            "adr_or_initiatives": 7,
        },
        {
            "id": "#05",
            "name": "DSCKI. Vũ Đức Thắng",
            "code_role": "Renal & Hepatic Dose Adjustment (Chỉnh liều Suy thận/Gan)",
            "subsystem": SUBSYSTEMS[1],
            "department": "Khoa Thận - Tiết niệu & Lọc máu",
            "personality": "Chính xác tuyệt đối với con số, cẩn thận, suy luận dược động học chặt chẽ",
            "competencies": "Tính eGFR, CrCl (Cockcroft-Gault), phân loại Child-Pugh, hiệu chỉnh liều cho bệnh nhân lọc máu/CRRT",
            "skill_score": 95,
            "phase": "Giai đoạn 1 (Cốt lõi)",
            "tasks_assigned": 140,
            "tasks_completed": 136,
            "acceptance_rate": 95.8,
            "sla_compliance": 96.0,
            "adr_or_initiatives": 6,
        },
        {
            "id": "#06",
            "name": "ThS.DS. Hoàng Minh Phương",
            "code_role": "Special Populations Safety (An toàn Thuốc Đối tượng Đặc biệt)",
            "subsystem": SUBSYSTEMS[1],
            "department": "Khoa Sản - Phụ khoa",
            "personality": "Chu đáo, ân cần, thấu cảm cao với bệnh nhân nhi, thai phụ và người cao tuổi",
            "competencies": "Thang an toàn thai kỳ FDA/TGA, tính liều nhi khoa theo cân nặng/BSA, bộ tiêu chuẩn Beers/STOPP-START",
            "skill_score": 91,
            "phase": "Giai đoạn 2 (Mở rộng)",
            "tasks_assigned": 125,
            "tasks_completed": 118,
            "acceptance_rate": 93.0,
            "sla_compliance": 94.5,
            "adr_or_initiatives": 5,
        },
        {
            "id": "#07",
            "name": "TS.DS. Đặng Quốc Khánh",
            "code_role": "Anti-infective & Stewardship (Dược lâm sàng Kháng sinh & ASP)",
            "subsystem": SUBSYSTEMS[2],
            "department": "Khoa Bệnh nhiệt đới & Truyền nhiễm",
            "personality": "Bản lĩnh, quyết liệt bảo vệ phác đồ chuẩn, lập luận vi sinh - dược lý thuyết phục",
            "competencies": "Quản lý sử dụng kháng sinh (ASP), đọc kháng sinh đồ, tư vấn xuống thang và chuyển kháng sinh IV sang PO",
            "skill_score": 97,
            "phase": "Giai đoạn 2 (Mở rộng)",
            "tasks_assigned": 160,
            "tasks_completed": 155,
            "acceptance_rate": 96.0,
            "sla_compliance": 95.0,
            "adr_or_initiatives": 10,
        },
        {
            "id": "#08",
            "name": "ThS.DS. Bùi Thanh Tùng",
            "code_role": "Therapeutic Drug Monitoring - TDM (Giám sát Nồng độ Thuốc)",
            "subsystem": SUBSYSTEMS[2],
            "department": "Khoa Hồi sức tích cực - Chống độc (ICU)",
            "personality": "Đam mê toán dược động học, tỉ mỉ, tập trung cao độ",
            "competencies": "Mô hình dược động học Bayes, hiệu chỉnh liều Vancomycin (AUC/MIC), Aminoglycosid, Phenytoin, Tacrolimus",
            "skill_score": 95,
            "phase": "Giai đoạn 2 (Mở rộng)",
            "tasks_assigned": 95,
            "tasks_completed": 92,
            "acceptance_rate": 97.2,
            "sla_compliance": 96.0,
            "adr_or_initiatives": 7,
        },
        {
            "id": "#09",
            "name": "DSCKI. Ngô Thị Lan Hương",
            "code_role": "Cardiology & Endocrinology (DLS Tim mạch & Nội tiết)",
            "subsystem": SUBSYSTEMS[2],
            "department": "Khoa Nội Tim mạch - Lão học",
            "personality": "Điềm đạm, sâu sắc, kiên trì đồng hành cùng bệnh nhân bệnh mạn tính",
            "competencies": "Tối ưu phác đồ suy tim, tăng huyết áp, đái tháo đường, kiểm soát HbA1c, lipid máu và thuốc chống đông",
            "skill_score": 92,
            "phase": "Giai đoạn 2 (Mở rộng)",
            "tasks_assigned": 145,
            "tasks_completed": 138,
            "acceptance_rate": 93.5,
            "sla_compliance": 95.0,
            "adr_or_initiatives": 6,
        },
        {
            "id": "#10",
            "name": "DSCKII. Trịnh Quang Huy",
            "code_role": "ICU & Emergency Critical Care (DLS Hồi sức Cấp cứu)",
            "subsystem": SUBSYSTEMS[2],
            "department": "Khoa Hồi sức tích cực - Chống độc (ICU)",
            "personality": "Bình tĩnh dưới áp lực cao, phản xạ lâm sàng tức thì, phối hợp ăn ý với bác sĩ trực",
            "competencies": "Thuốc vận mạch, an thần - giảm đau ICU, tra cứu tương kỵ truyền tĩnh mạch chữ Y (Y-site), đánh giá SOFA",
            "skill_score": 96,
            "phase": "Giai đoạn 2 (Mở rộng)",
            "tasks_assigned": 130,
            "tasks_completed": 126,
            "acceptance_rate": 96.8,
            "sla_compliance": 98.5,
            "adr_or_initiatives": 9,
        },
        {
            "id": "#11",
            "name": "ThS.DS. Lý Mỹ Linh",
            "code_role": "Oncology & Supportive Care (DLS Ung bướu & Huyết học)",
            "subsystem": SUBSYSTEMS[2],
            "department": "Khoa Ung bướu & Huyết học lâm sàng",
            "personality": "Kỹ lưỡng, giàu lòng trắc ẩn, kiểm tra chéo đa tầng không để xảy ra sai sót",
            "competencies": "Kiểm duyệt liều hóa trị/nhắm trúng đích theo BSA, dự phòng nôn, xử trí sốt giảm bạch cầu hạt (ANC)",
            "skill_score": 93,
            "phase": "Giai đoạn 3 (Hoàn thiện)",
            "tasks_assigned": 100,
            "tasks_completed": 95,
            "acceptance_rate": 95.0,
            "sla_compliance": 96.0,
            "adr_or_initiatives": 5,
        },
        {
            "id": "#12",
            "name": "DSCKI. Đỗ Văn Khôi",
            "code_role": "Pain Management & Palliative Care (Quản lý Đau & Giảm nhẹ)",
            "subsystem": SUBSYSTEMS[2],
            "department": "Đơn vị Quản lý Đau & Chăm sóc giảm nhẹ",
            "personality": "Nhẹ nhàng, lắng nghe, thấu hiểu tâm lý người bệnh đau mạn tính",
            "competencies": "Thang điểm đau VAS/NPRS, tính chuyển đổi liều tương đương Opioid (MME), dự phòng ức chế hô hấp & táo bón",
            "skill_score": 89,
            "phase": "Giai đoạn 3 (Hoàn thiện)",
            "tasks_assigned": 85,
            "tasks_completed": 80,
            "acceptance_rate": 91.5,
            "sla_compliance": 94.0,
            "adr_or_initiatives": 4,
        },
        {
            "id": "#13",
            "name": "ThS.DS. Mai Thanh Thảo",
            "code_role": "Medical Literature & RAG Query (Tra cứu Dược thư & Phác đồ)",
            "subsystem": SUBSYSTEMS[3],
            "department": "Trung tâm Thông tin thuốc & Cảnh giác Dược (DI & ADR)",
            "personality": "Ham học hỏi, tư duy học thuật chuẩn mực, trích dẫn bằng chứng y khoa chính xác",
            "competencies": "Truy xuất Dược thư Quốc gia, Micromedex, AHFS, Hướng dẫn Bộ Y tế, tổng hợp điểm tin thông tin thuốc",
            "skill_score": 94,
            "phase": "Giai đoạn 1 (Cốt lõi)",
            "tasks_assigned": 170,
            "tasks_completed": 165,
            "acceptance_rate": 96.0,
            "sla_compliance": 97.5,
            "adr_or_initiatives": 8,
        },
        {
            "id": "#14",
            "name": "DSCKI. Phan Anh Tuấn",
            "code_role": "Pharmacovigilance & ADR Reporting (Cảnh giác Dược & ADR)",
            "subsystem": SUBSYSTEMS[3],
            "department": "Trung tâm Thông tin thuốc & Cảnh giác Dược (DI & ADR)",
            "personality": "Bền bỉ, tinh thần cảnh giác cao, phân tích nguyên nhân - hệ quả khách quan",
            "competencies": "Đánh giá thang Naranjo và WHO-UMC, lập báo cáo ADR gửi Trung tâm DI & ADR Quốc gia, truy vết chuỗi phản ứng",
            "skill_score": 92,
            "phase": "Giai đoạn 2 (Mở rộng)",
            "tasks_assigned": 90,
            "tasks_completed": 87,
            "acceptance_rate": 94.0,
            "sla_compliance": 96.0,
            "adr_or_initiatives": 14,
        },
        {
            "id": "#15",
            "name": "DSĐH. Nguyễn Bảo Ngọc",
            "code_role": "Patient Medication Education (Tư vấn & Hướng dẫn Bệnh nhân)",
            "subsystem": SUBSYSTEMS[3],
            "department": "Khoa Khám bệnh & Điều trị Ngoại trú",
            "personality": "Hoạt ngôn, truyền cảm, biến kiến thức y khoa phức tạp thành lời khuyên dễ hiểu",
            "competencies": "Tư vấn kỹ thuật dùng bình hít/xịt COPD-Hen, bút tiêm Insulin, thời điểm dùng thuốc và chế độ dinh dưỡng",
            "skill_score": 90,
            "phase": "Giai đoạn 3 (Hoàn thiện)",
            "tasks_assigned": 200,
            "tasks_completed": 190,
            "acceptance_rate": 94.0,
            "sla_compliance": 95.0,
            "adr_or_initiatives": 6,
        },
        {
            "id": "#16",
            "name": "DSĐH. Trương Gia Bảo",
            "code_role": "Digital Adherence & Refill Monitor (Theo dõi Tuân thủ Điều trị)",
            "subsystem": SUBSYSTEMS[3],
            "department": "Khoa Nội tiết - Đái tháo đường",
            "personality": "Nhiệt tình, kỷ luật, tận tâm đồng hành cùng bệnh nhân ngoại trú",
            "competencies": "Đánh giá tuân thủ điều trị theo thang MMAS-8, quản lý lịch nhắc uống thuốc Telehealth, cảnh báo bỏ liều",
            "skill_score": 88,
            "phase": "Giai đoạn 3 (Hoàn thiện)",
            "tasks_assigned": 160,
            "tasks_completed": 148,
            "acceptance_rate": 90.5,
            "sla_compliance": 93.5,
            "adr_or_initiatives": 4,
        },
        {
            "id": "#17",
            "name": "DSCKI. Hà Kiều Trang",
            "code_role": "Health Insurance & Formulary Compliance (Kiểm soát BHYT)",
            "subsystem": SUBSYSTEMS[4],
            "department": "Phòng Bảo hiểm Y tế & Kinh tế Dược",
            "personality": "Sắc sảo, nắm vững thông tư, bảo vệ an toàn quỹ BHYT và quyền lợi người bệnh",
            "competencies": "Rà soát điều kiện thanh toán BHYT theo Thông tư 20/2022/TT-BYT, phòng ngừa xuất toán thuốc ngoài danh mục",
            "skill_score": 95,
            "phase": "Giai đoạn 1 (Cốt lõi)",
            "tasks_assigned": 190,
            "tasks_completed": 185,
            "acceptance_rate": 97.0,
            "sla_compliance": 98.0,
            "adr_or_initiatives": 7,
        },
        {
            "id": "#18",
            "name": "ThS.DS. Lương Thế Vinh",
            "code_role": "Pharmacoeconomics & Cost-Optimization (Kinh tế Dược)",
            "subsystem": SUBSYSTEMS[4],
            "department": "Phòng Bảo hiểm Y tế & Kinh tế Dược",
            "personality": "Thực tế, tư duy tối ưu hóa nguồn lực, cân bằng hiệu quả điều trị và chi phí",
            "competencies": "Phân tích chi phí - hiệu quả (CEA), tư vấn chuyển đổi thuốc Generic/Biosimilar, phân tích ABC/VEN",
            "skill_score": 91,
            "phase": "Giai đoạn 3 (Hoàn thiện)",
            "tasks_assigned": 105,
            "tasks_completed": 98,
            "acceptance_rate": 91.0,
            "sla_compliance": 94.0,
            "adr_or_initiatives": 5,
        },
        {
            "id": "#19",
            "name": "TS.DS. Chu Hoàng Yến",
            "code_role": "Clinical Audit & DUE/DUR (Đánh giá Sử dụng Thuốc & NCKH)",
            "subsystem": SUBSYSTEMS[4],
            "department": "Trung tâm Đào tạo & Nghiên cứu Khoa học",
            "personality": "Tư duy dữ liệu lớn, sắc bén trong nghiên cứu khoa học và cải tiến chất lượng",
            "competencies": "Thiết kế đề cương DUE/DUR, thống kê y sinh, kiểm toán đơn thuốc toàn viện, viết báo cáo NCKH",
            "skill_score": 94,
            "phase": "Giai đoạn 3 (Hoàn thiện)",
            "tasks_assigned": 75,
            "tasks_completed": 72,
            "acceptance_rate": 95.5,
            "sla_compliance": 96.0,
            "adr_or_initiatives": 9,
        },
        {
            "id": "#20",
            "name": "ThS.DS. Nguyễn Xuân Bách",
            "code_role": "Pharmacist Continuing Education - CME (Đào tạo Liên tục)",
            "subsystem": SUBSYSTEMS[4],
            "department": "Trung tâm Đào tạo & Nghiên cứu Khoa học",
            "personality": "Truyền cảm hứng, sáng tạo, luôn cập nhật xu hướng y học thực chứng mới nhất",
            "competencies": "Xây dựng ngân hàng ca lâm sàng (Case Study), tổ chức sinh hoạt khoa học CME, cập nhật PubMed/Guideline",
            "skill_score": 91,
            "phase": "Giai đoạn 3 (Hoàn thiện)",
            "tasks_assigned": 80,
            "tasks_completed": 76,
            "acceptance_rate": 93.0,
            "sla_compliance": 95.0,
            "adr_or_initiatives": 8,
        },
    ]


def get_default_tasks():
    return [
        {
            "task_id": "CV-001",
            "member_id": "#01",
            "member_name": "DSCKII. Nguyễn Minh Quân",
            "department": "Ban Giám đốc & Phòng KHTH (Điều phối chung)",
            "task_title": "Điều phối hội chẩn Dược lâm sàng 15 ca bệnh nặng liên khoa",
            "workflow_step": WORKFLOW_STEPS[0],
            "priority": "Khẩn cấp",
            "status": "Hoàn thành",
            "progress": 100,
            "deadline": "2026-11-10",
            "kpi_quality": 98,
        },
        {
            "task_id": "CV-002",
            "member_id": "#02",
            "member_name": "ThS.DS. Trần Thu Hà",
            "department": "Ban Giám đốc & Phòng KHTH (Điều phối chung)",
            "task_title": "Rà soát tuân thủ quy trình SOP Dược lâm sàng theo Nghị định 131/2020/NĐ-CP",
            "workflow_step": WORKFLOW_STEPS[2],
            "priority": "Cao",
            "status": "Hoàn thành",
            "progress": 100,
            "deadline": "2026-11-12",
            "kpi_quality": 97,
        },
        {
            "task_id": "CV-003",
            "member_id": "#03",
            "member_name": "DSCKI. Lê Hoàng Nam",
            "department": "Khoa Khám bệnh & Điều trị Ngoại trú",
            "task_title": "Khai thác và đối soát tiền sử dùng thuốc (MedRec) cho 40 bệnh nhân mới nhập viện",
            "workflow_step": WORKFLOW_STEPS[0],
            "priority": "Cao",
            "status": "Đang thực hiện",
            "progress": 85,
            "deadline": "2026-11-14",
            "kpi_quality": 92,
        },
        {
            "task_id": "CV-004",
            "member_id": "#04",
            "member_name": "ThS.DS. Phạm Ngọc Ánh",
            "department": "Khoa Nội Hô hấp - Tiêu hóa",
            "task_title": "Rà soát tương tác thuốc chống chỉ định trên 120 đơn thuốc nội trú & ngoại trú",
            "workflow_step": WORKFLOW_STEPS[1],
            "priority": "Khẩn cấp",
            "status": "Hoàn thành",
            "progress": 100,
            "deadline": "2026-11-11",
            "kpi_quality": 95,
        },
        {
            "task_id": "CV-005",
            "member_id": "#05",
            "member_name": "DSCKI. Vũ Đức Thắng",
            "department": "Khoa Thận - Tiết niệu & Lọc máu",
            "task_title": "Tính CrCl/eGFR và hiệu chỉnh liều thuốc cho 28 bệnh nhân suy thận mạn & lọc máu chu kỳ",
            "workflow_step": WORKFLOW_STEPS[1],
            "priority": "Khẩn cấp",
            "status": "Đang thực hiện",
            "progress": 90,
            "deadline": "2026-11-12",
            "kpi_quality": 96,
        },
        {
            "task_id": "CV-006",
            "member_id": "#06",
            "member_name": "ThS.DS. Hoàng Minh Phương",
            "department": "Khoa Sản - Phụ khoa",
            "task_title": "Kiểm duyệt an toàn thuốc cho thai phụ nguy cơ cao & sàng lọc tiêu chuẩn Beers lão khoa",
            "workflow_step": WORKFLOW_STEPS[1],
            "priority": "Cao",
            "status": "Đang thực hiện",
            "progress": 80,
            "deadline": "2026-11-15",
            "kpi_quality": 93,
        },
        {
            "task_id": "CV-007",
            "member_id": "#07",
            "member_name": "TS.DS. Đặng Quốc Khánh",
            "department": "Khoa Bệnh nhiệt đới & Truyền nhiễm",
            "task_title": "Duyệt kháng sinh ưu tiên quản lý (Meropenem, Colistin, Linezolid) & tư vấn xuống thang theo kháng sinh đồ",
            "workflow_step": WORKFLOW_STEPS[1],
            "priority": "Khẩn cấp",
            "status": "Hoàn thành",
            "progress": 100,
            "deadline": "2026-11-11",
            "kpi_quality": 97,
        },
        {
            "task_id": "CV-008",
            "member_id": "#08",
            "member_name": "ThS.DS. Bùi Thanh Tùng",
            "department": "Khoa Hồi sức tích cực - Chống độc (ICU)",
            "task_title": "Giám sát nồng độ Vancomycin & Amikacin trong máu (TDM) bằng phần mềm dược động học Bayes",
            "workflow_step": WORKFLOW_STEPS[1],
            "priority": "Khẩn cấp",
            "status": "Đang thực hiện",
            "progress": 92,
            "deadline": "2026-11-12",
            "kpi_quality": 96,
        },
        {
            "task_id": "CV-009",
            "member_id": "#09",
            "member_name": "DSCKI. Ngô Thị Lan Hương",
            "department": "Khoa Nội Tim mạch - Lão học",
            "task_title": "Tối ưu phác đồ tứ trụ suy tim HFrEF và kiểm soát liều thuốc chống đông NOAC/Kháng Vitamin K",
            "workflow_step": WORKFLOW_STEPS[1],
            "priority": "Cao",
            "status": "Đang thực hiện",
            "progress": 88,
            "deadline": "2026-11-15",
            "kpi_quality": 94,
        },
        {
            "task_id": "CV-010",
            "member_id": "#10",
            "member_name": "DSCKII. Trịnh Quang Huy",
            "department": "Khoa Hồi sức tích cực - Chống độc (ICU)",
            "task_title": "Đi buồng lâm sàng ICU, lập bảng tương kỵ pha truyền tĩnh mạch chữ Y (Y-site) cho bệnh nhân sốc nhiễm khuẩn",
            "workflow_step": WORKFLOW_STEPS[1],
            "priority": "Khẩn cấp",
            "status": "Hoàn thành",
            "progress": 100,
            "deadline": "2026-11-10",
            "kpi_quality": 98,
        },
        {
            "task_id": "CV-011",
            "member_id": "#11",
            "member_name": "ThS.DS. Lý Mỹ Linh",
            "department": "Khoa Ung bướu & Huyết học lâm sàng",
            "task_title": "Kiểm tra chéo liều hóa chất theo diện tích da (BSA) và phác đồ chống nôn CINV",
            "workflow_step": WORKFLOW_STEPS[1],
            "priority": "Khẩn cấp",
            "status": "Chờ duyệt HITL",
            "progress": 95,
            "deadline": "2026-11-13",
            "kpi_quality": 95,
        },
        {
            "task_id": "CV-012",
            "member_id": "#12",
            "member_name": "DSCKI. Đỗ Văn Khôi",
            "department": "Đơn vị Quản lý Đau & Chăm sóc giảm nhẹ",
            "task_title": "Chuyển đổi liều tương đương Morphin - Fentanyl và dự phòng táo bón do Opioid",
            "workflow_step": WORKFLOW_STEPS[1],
            "priority": "Trung bình",
            "status": "Đang thực hiện",
            "progress": 78,
            "deadline": "2026-11-16",
            "kpi_quality": 91,
        },
        {
            "task_id": "CV-013",
            "member_id": "#13",
            "member_name": "ThS.DS. Mai Thanh Thảo",
            "department": "Trung tâm Thông tin thuốc & Cảnh giác Dược (DI & ADR)",
            "task_title": "Số hóa 35 chuyên luận Dược thư Quốc gia và trả lời 20 câu hỏi Thông tin thuốc cho các khoa",
            "workflow_step": WORKFLOW_STEPS[4],
            "priority": "Cao",
            "status": "Hoàn thành",
            "progress": 100,
            "deadline": "2026-11-12",
            "kpi_quality": 96,
        },
        {
            "task_id": "CV-014",
            "member_id": "#14",
            "member_name": "DSCKI. Phan Anh Tuấn",
            "department": "Trung tâm Thông tin thuốc & Cảnh giác Dược (DI & ADR)",
            "task_title": "Thẩm định nguyên nhân 12 báo cáo ADR theo thang Naranjo và gửi cổng Quốc gia",
            "workflow_step": WORKFLOW_STEPS[4],
            "priority": "Cao",
            "status": "Hoàn thành",
            "progress": 100,
            "deadline": "2026-11-11",
            "kpi_quality": 95,
        },
        {
            "task_id": "CV-015",
            "member_id": "#15",
            "member_name": "DSĐH. Nguyễn Bảo Ngọc",
            "department": "Khoa Khám bệnh & Điều trị Ngoại trú",
            "task_title": "Tư vấn trực tiếp kỹ thuật sử dụng bình hít COPD và bút tiêm Insulin cho 65 bệnh nhân ngoại trú",
            "workflow_step": WORKFLOW_STEPS[4],
            "priority": "Cao",
            "status": "Đang thực hiện",
            "progress": 88,
            "deadline": "2026-11-15",
            "kpi_quality": 93,
        },
        {
            "task_id": "CV-016",
            "member_id": "#16",
            "member_name": "DSĐH. Trương Gia Bảo",
            "department": "Khoa Nội tiết - Đái tháo đường",
            "task_title": "Đánh giá điểm tuân thủ dùng thuốc MMAS-8 và vận hành hệ thống nhắc lịch tái khám",
            "workflow_step": WORKFLOW_STEPS[4],
            "priority": "Trung bình",
            "status": "Đang thực hiện",
            "progress": 82,
            "deadline": "2026-11-18",
            "kpi_quality": 90,
        },
        {
            "task_id": "CV-017",
            "member_id": "#17",
            "member_name": "DSCKI. Hà Kiều Trang",
            "department": "Phòng Bảo hiểm Y tế & Kinh tế Dược",
            "task_title": "Kiểm soát điều kiện thanh toán BHYT theo Thông tư 20/2022/TT-BYT đối với thuốc chi phí lớn",
            "workflow_step": WORKFLOW_STEPS[2],
            "priority": "Khẩn cấp",
            "status": "Hoàn thành",
            "progress": 100,
            "deadline": "2026-11-10",
            "kpi_quality": 97,
        },
        {
            "task_id": "CV-018",
            "member_id": "#18",
            "member_name": "ThS.DS. Lương Thế Vinh",
            "department": "Phòng Bảo hiểm Y tế & Kinh tế Dược",
            "task_title": "Phân tích ABC/VEN quý IV và đề xuất danh mục chuyển đổi thuốc Generic tiết kiệm chi phí",
            "workflow_step": WORKFLOW_STEPS[2],
            "priority": "Cao",
            "status": "Đang thực hiện",
            "progress": 84,
            "deadline": "2026-11-17",
            "kpi_quality": 92,
        },
        {
            "task_id": "CV-019",
            "member_id": "#19",
            "member_name": "TS.DS. Chu Hoàng Yến",
            "department": "Trung tâm Đào tạo & Nghiên cứu Khoa học",
            "task_title": "Thực hiện chuyên đề đánh giá sử dụng thuốc (DUE) nhóm kháng sinh dự trữ toàn viện",
            "workflow_step": WORKFLOW_STEPS[4],
            "priority": "Cao",
            "status": "Chờ duyệt HITL",
            "progress": 94,
            "deadline": "2026-11-16",
            "kpi_quality": 96,
        },
        {
            "task_id": "CV-020",
            "member_id": "#20",
            "member_name": "ThS.DS. Nguyễn Xuân Bách",
            "department": "Trung tâm Đào tạo & Nghiên cứu Khoa học",
            "task_title": "Biên soạn 5 ca lâm sàng giả lập (Case Study) và tổ chức tập huấn CME tháng 11",
            "workflow_step": WORKFLOW_STEPS[4],
            "priority": "Trung bình",
            "status": "Hoàn thành",
            "progress": 100,
            "deadline": "2026-11-14",
            "kpi_quality": 94,
        },
    ]


# Khởi tạo Session State
if "members" not in st.session_state:
    st.session_state.members = get_default_members()

if "tasks" not in st.session_state:
    st.session_state.tasks = get_default_tasks()


def compute_kpi_dataframe(members_list, tasks_list, w_progress, w_quality, w_sla):
    df_m = pd.DataFrame(members_list)
    df_t = pd.DataFrame(tasks_list)

    if not df_t.empty:
        task_agg = (
            df_t.groupby("member_id")
            .agg(
                num_tasks=("task_id", "count"),
                avg_task_progress=("progress", "mean"),
                avg_task_quality=("kpi_quality", "mean"),
            )
            .reset_index()
        )
        df_m = df_m.merge(task_agg, left_on="id", right_on="member_id", how="left")
        df_m["num_tasks"] = df_m["num_tasks"].fillna(0).astype(int)
        df_m["avg_task_progress"] = df_m["avg_task_progress"].fillna(
            (df_m["tasks_completed"] / df_m["tasks_assigned"].replace(0, 1)) * 100
        )
    else:
        df_m["num_tasks"] = 0
        df_m["avg_task_progress"] = (
            df_m["tasks_completed"] / df_m["tasks_assigned"].replace(0, 1)
        ) * 100

    df_m["completion_rate"] = (
        (df_m["tasks_completed"] / df_m["tasks_assigned"].replace(0, 1)) * 100
    ).clip(0, 100)

    df_m["progress_score"] = (
        0.6 * df_m["completion_rate"] + 0.4 * df_m["avg_task_progress"]
    ).round(1)

    total_w = max(w_progress + w_quality + w_sla, 1)
    df_m["kpi_total"] = (
        (
            df_m["progress_score"] * w_progress
            + df_m["acceptance_rate"] * w_quality
            + df_m["sla_compliance"] * w_sla
        )
        / total_w
    ).round(1)

    def classify_kpi(score):
        if score >= 95:
            return "Xuất sắc (A+)"
        elif score >= 90:
            return "Tốt (A)"
        elif score >= 80:
            return "Đạt chuẩn (B)"
        else:
            return "Cần cải thiện (C)"

    df_m["kpi_rank"] = df_m["kpi_total"].apply(classify_kpi)
    return df_m


# ==========================================
# 2. THANH BÊN (SIDEBAR): ĐIỀU KHIỂN & LỌC DỮ LIỆU
# ==========================================
with st.sidebar:
    st.markdown("## 🏥 TỔ DƯỢC LÂM SÀNG 20 NGƯỜI")
    st.caption(
        "Mô hình Đa tác tử & Nhân sự Dược lâm sàng chuẩn Nghị định 131/2020/NĐ-CP"
    )

    selected_subsystem = st.multiselect(
        "Lọc theo Phân hệ Chuyên môn",
        options=SUBSYSTEMS,
        default=SUBSYSTEMS,
    )

    all_depts = sorted(list({m["department"] for m in st.session_state.members}))
    selected_depts = st.multiselect(
        "Lọc theo Khoa Lâm sàng phụ trách",
        options=all_depts,
        default=all_depts,
    )

    st.markdown("### ⚙️ Cấu hình Trọng số KPI (%)")
    w_progress = st.slider("Trọng số Tiến độ & Khối lượng", 10, 70, 40, 5)
    w_quality = st.slider("Trọng số Chất lượng (BS đồng thuận)", 10, 70, 35, 5)
    w_sla = st.slider("Trọng số Tuân thủ SLA & Quy chuẩn", 10, 60, 25, 5)
    st.caption(f"Tổng trọng số quy chuẩn: **{w_progress + w_quality + w_sla}%**")

    st.markdown("### 💾 Sao lưu & Khôi phục Cấu hình")
    export_payload = {
        "updated_at": datetime.now().isoformat(),
        "members": st.session_state.members,
        "tasks": st.session_state.tasks,
    }
    st.download_button(
        label="⬇️ Tải xuống Cấu hình (JSON)",
        data=json.dumps(export_payload, ensure_ascii=False, indent=2),
        file_name="to_duoc_lam_sang_20_nguoi.json",
        mime="application/json",
        use_container_width=True,
    )

    uploaded_json = st.file_uploader("⬆️ Nạp cấu hình đã lưu (.json)", type=["json"])
    if uploaded_json is not None:
        try:
            loaded_data = json.load(uploaded_json)
            if "members" in loaded_data and "tasks" in loaded_data:
                st.session_state.members = loaded_data["members"]
                st.session_state.tasks = loaded_data["tasks"]
                st.success("Đã nạp thành công dữ liệu 20 thành viên và công việc!")
        except Exception as e:
            st.error(f"Lỗi đọc file JSON: {e}")

    if st.button("🔄 Khôi phục Dữ liệu Mặc định", use_container_width=True):
        st.session_state.members = get_default_members()
        st.session_state.tasks = get_default_tasks()
        st.rerun()

# Tính toán bảng tổng hợp KPI
df_kpi_all = compute_kpi_dataframe(
    st.session_state.members,
    st.session_state.tasks,
    w_progress,
    w_quality,
    w_sla,
)

df_filtered = df_kpi_all[
    df_kpi_all["subsystem"].isin(selected_subsystem)
    & df_kpi_all["department"].isin(selected_depts)
].copy()

# ==========================================
# 3. TIÊU ĐỀ CHÍNH & CHỈ SỐ TỔNG QUAN (TOP METRICS)
# ==========================================
st.title("🏥 Hệ Thống Quản Trị Tổ Dược Lâm Sàng 20 Thành Viên")
st.markdown(
    "**Thiết lập Tính cách, Năng lực, Phân công Khoa Lâm sàng, Theo dõi Tiến độ Công việc & Đánh giá KPI toàn diện**"
)

col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
with col_m1:
    st.metric(
        "Tổng nhân sự Tổ DLS",
        f"{len(df_filtered)} / 20 người",
        "5 Phân hệ chuyên môn",
    )
with col_m2:
    total_assigned = int(df_filtered["tasks_assigned"].sum())
    total_done = int(df_filtered["tasks_completed"].sum())
    rate_done = round((total_done / max(total_assigned, 1)) * 100, 1)
    st.metric("Ca lâm sàng đã xử lý", f"{total_done}/{total_assigned}", f"{rate_done}% hoàn thành")
with col_m3:
    avg_accept = round(df_filtered["acceptance_rate"].mean(), 1) if not df_filtered.empty else 0.0
    st.metric("Tỷ lệ BS chấp thuận tư vấn", f"{avg_accept}%", "+2.4% so với mục tiêu")
with col_m4:
    avg_kpi = round(df_filtered["kpi_total"].mean(), 1) if not df_filtered.empty else 0.0
    st.metric("Điểm KPI Trung bình Tổ", f"{avg_kpi} / 100", "Chuẩn NĐ 131/2020/NĐ-CP")
with col_m5:
    count_a_plus = int((df_filtered["kpi_rank"] == "Xuất sắc (A+)").sum())
    st.metric("Nhân sự Xuất sắc (A+)", f"{count_a_plus} thành viên", "Đạt chuẩn chất lượng cao")

# ==========================================
# 4. CÁC PHÂN KHU CHỨC NĂNG (TABS)
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "👥 1. Cài đặt 20 Thành viên (Tính cách, Năng lực & Khoa)",
        "📋 2. Phân công Công việc & Tiến độ",
        "📊 3. Bảng Đánh giá KPI & Biểu đồ Phân tích",
        "🔄 4. Quy trình Phối hợp 5 Bước & Kiến trúc Hệ thống",
    ]
)

# ------------------------------------------
# TAB 1: CÀI ĐẶT 20 THÀNH VIÊN
# ------------------------------------------
with tab1:
    st.subheader("⚙️ Hồ sơ & Cài đặt Tính cách, Năng lực, Phân công Khoa Lâm sàng (20 Thành viên)")
    st.info(
        "💡 **Hướng dẫn:** Bạn có thể bấm đúp vào từng ô trong bảng bên dưới để sửa nhanh **Họ tên, Khoa lâm sàng, Tính cách, Năng lực**, hoặc dùng khung **Cài đặt chi tiết từng bạn** ở phía dưới để chỉnh sửa sâu cho từng thành viên."
    )

    editable_cols = [
        "id",
        "name",
        "code_role",
        "subsystem",
        "department",
        "personality",
        "competencies",
        "skill_score",
        "phase",
    ]
    df_members_edit = pd.DataFrame(st.session_state.members)[editable_cols]

    edited_members_df = st.data_editor(
        df_members_edit,
        column_config={
            "id": st.column_config.TextColumn("Mã số", disabled=True, width="small"),
            "name": st.column_config.TextColumn("Họ và tên Dược sĩ / Định danh", width="medium"),
            "code_role": st.column_config.TextColumn("Chức danh trong Tổ DLS", width="medium"),
            "subsystem": st.column_config.SelectboxColumn(
                "Phân hệ Chuyên môn", options=SUBSYSTEMS, width="medium"
            ),
            "department": st.column_config.SelectboxColumn(
                "Phân công Khoa Lâm sàng", options=CLINICAL_DEPARTMENTS, width="medium"
            ),
            "personality": st.column_config.TextColumn("Tính cách & Phong cách làm việc", width="large"),
            "competencies": st.column_config.TextColumn("Năng lực chuyên môn & Công cụ lõi", width="large"),
            "skill_score": st.column_config.NumberColumn(
                "Điểm Năng lực (0-100)", min_value=0, max_value=100, step=1, width="small"
            ),
            "phase": st.column_config.SelectboxColumn(
                "Giai đoạn triển khai",
                options=["Giai đoạn 1 (Cốt lõi)", "Giai đoạn 2 (Mở rộng)", "Giai đoạn 3 (Hoàn thiện)"],
                width="small",
            ),
        },
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        key="members_table_editor",
    )

    if st.button("💾 Lưu thay đổi từ Bảng Nhân sự", type="primary"):
        for idx, row in edited_members_df.iterrows():
            for col in editable_cols:
                st.session_state.members[idx][col] = row[col]
        st.success("Đã cập nhật thông tin Tính cách, Năng lực và Khoa lâm sàng cho 20 thành viên!")
        st.rerun()

    st.markdown("### 🧑‍⚕️ Chỉnh sửa Hồ sơ Chi tiết Từng Thành viên")
    member_labels = [
        f"{m['id']} - {m['name']} ({m['code_role']})" for m in st.session_state.members
    ]
    selected_idx = st.selectbox(
        "Chọn thành viên để cài đặt chi tiết:",
        options=range(len(member_labels)),
        format_func=lambda i: member_labels[i],
    )

    current_m = st.session_state.members[selected_idx]
    with st.form(key=f"detail_member_form_{current_m['id']}"):
        c1, c2, c3 = st.columns(3)
        with c1:
            new_name = st.text_input("Họ tên Dược sĩ / Tên Agent", value=current_m["name"])
            new_role = st.text_input("Chức danh chuyên môn", value=current_m["code_role"])
        with c2:
            dept_options = list(CLINICAL_DEPARTMENTS)
            if current_m["department"] not in dept_options:
                dept_options.append(current_m["department"])
            new_dept = st.selectbox(
                "Khoa Lâm sàng phân công",
                options=dept_options,
                index=dept_options.index(current_m["department"]),
            )
            new_sub = st.selectbox(
                "Phân hệ quản lý",
                options=SUBSYSTEMS,
                index=SUBSYSTEMS.index(current_m["subsystem"])
                if current_m["subsystem"] in SUBSYSTEMS
                else 0,
            )
        with c3:
            new_skill_score = st.slider(
                "Điểm đánh giá năng lực cốt lõi",
                min_value=50,
                max_value=100,
                value=int(current_m["skill_score"]),
            )
            new_phase = st.selectbox(
                "Lộ trình triển khai",
                options=["Giai đoạn 1 (Cốt lõi)", "Giai đoạn 2 (Mở rộng)", "Giai đoạn 3 (Hoàn thiện)"],
                index=["Giai đoạn 1 (Cốt lõi)", "Giai đoạn 2 (Mở rộng)", "Giai đoạn 3 (Hoàn thiện)"].index(
                    current_m["phase"]
                )
                if current_m["phase"]
                in ["Giai đoạn 1 (Cốt lõi)", "Giai đoạn 2 (Mở rộng)", "Giai đoạn 3 (Hoàn thiện)"]
                else 0,
            )

        new_personality = st.text_area(
            "Tính cách & Phong cách phối hợp lâm sàng",
            value=current_m["personality"],
            height=80,
        )
        new_competencies = st.text_area(
            "Năng lực chuyên môn, Thuật toán & Công cụ sử dụng",
            value=current_m["competencies"],
            height=80,
        )

        submitted_member = st.form_submit_button("✅ Cập nhật Hồ sơ Thành viên này")
        if submitted_member:
            st.session_state.members[selected_idx].update(
                {
                    "name": new_name,
                    "code_role": new_role,
                    "department": new_dept,
                    "subsystem": new_sub,
                    "skill_score": new_skill_score,
                    "phase": new_phase,
                    "personality": new_personality,
                    "competencies": new_competencies,
                }
            )
            for t in st.session_state.tasks:
                if t["member_id"] == current_m["id"]:
                    t["member_name"] = new_name
            st.success(f"Đã lưu cài đặt cho {current_m['id']} - {new_name}!")
            st.rerun()

# ------------------------------------------
# TAB 2: PHÂN CÔNG CÔNG VIỆC & TIẾN ĐỘ
# ------------------------------------------
with tab2:
    st.subheader("📋 Quản lý Công việc Được giao & Theo dõi Tiến độ Thực hiện")

    with st.expander("➕ Giao Công việc Mới cho Thành viên Tổ Dược Lâm Sàng", expanded=False):
        with st.form("add_task_form"):
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                chosen_m_idx = st.selectbox(
                    "Giao cho thành viên",
                    options=range(len(st.session_state.members)),
                    format_func=lambda i: f"{st.session_state.members[i]['id']} - {st.session_state.members[i]['name']}",
                )
                chosen_member = st.session_state.members[chosen_m_idx]
                task_dept = st.selectbox(
                    "Khoa Lâm sàng thực hiện",
                    options=CLINICAL_DEPARTMENTS,
                    index=CLINICAL_DEPARTMENTS.index(chosen_member["department"])
                    if chosen_member["department"] in CLINICAL_DEPARTMENTS
                    else 0,
                )
            with fc2:
                task_step = st.selectbox("Thuộc Bước quy trình", options=WORKFLOW_STEPS)
                task_priority = st.selectbox(
                    "Mức độ ưu tiên", options=["Khẩn cấp", "Cao", "Trung bình", "Thấp"]
                )
            with fc3:
                task_deadline = st.date_input("Hạn hoàn thành", value=date(2026, 11, 20))
                task_progress = st.slider("Tiến độ ban đầu (%)", 0, 100, 20, 5)

            task_title = st.text_input(
                "Nội dung công việc cụ thể",
                placeholder="VD: Hội chẩn kháng sinh dự trữ và tính liều Vancomycin cho 5 bệnh nhân khoa ICU...",
            )
            add_task_btn = st.form_submit_button("📌 Giao việc ngay")
            if add_task_btn:
                if not task_title.strip():
                    st.warning("Vui lòng nhập nội dung công việc!")
                else:
                    new_id = f"CV-{len(st.session_state.tasks) + 1:03d}"
                    status_val = "Hoàn thành" if task_progress == 100 else "Đang thực hiện"
                    st.session_state.tasks.append(
                        {
                            "task_id": new_id,
                            "member_id": chosen_member["id"],
                            "member_name": chosen_member["name"],
                            "department": task_dept,
                            "task_title": task_title.strip(),
                            "workflow_step": task_step,
                            "priority": task_priority,
                            "status": status_val,
                            "progress": task_progress,
                            "deadline": str(task_deadline),
                            "kpi_quality": 95,
                        }
                    )
                    st.success(f"Đã giao công việc {new_id} cho {chosen_member['name']}!")
                    st.rerun()

    # Bộ lọc nhanh cho bảng công việc
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        status_filter = st.multiselect(
            "Trạng thái công việc",
            options=["Chưa bắt đầu", "Đang thực hiện", "Chờ duyệt HITL", "Hoàn thành", "Quá hạn"],
            default=["Chưa bắt đầu", "Đang thực hiện", "Chờ duyệt HITL", "Hoàn thành", "Quá hạn"],
        )
    with f_col2:
        priority_filter = st.multiselect(
            "Mức độ ưu tiên",
            options=["Khẩn cấp", "Cao", "Trung bình", "Thấp"],
            default=["Khẩn cấp", "Cao", "Trung bình", "Thấp"],
        )
    with f_col3:
        member_filter_ids = [m["id"] for m in st.session_state.members]
        selected_member_ids = st.multiselect(
            "Thành viên phụ trách",
            options=member_filter_ids,
            default=member_filter_ids,
        )

    df_tasks = pd.DataFrame(st.session_state.tasks)
    df_tasks_view = df_tasks[
        df_tasks["status"].isin(status_filter)
        & df_tasks["priority"].isin(priority_filter)
        & df_tasks["member_id"].isin(selected_member_ids)
    ].copy()

    edited_tasks_df = st.data_editor(
        df_tasks_view,
        column_config={
            "task_id": st.column_config.TextColumn("Mã CV", disabled=True, width="small"),
            "member_id": st.column_config.TextColumn("Mã TV", disabled=True, width="small"),
            "member_name": st.column_config.TextColumn("Người phụ trách", disabled=True, width="medium"),
            "department": st.column_config.SelectboxColumn(
                "Khoa Lâm sàng", options=CLINICAL_DEPARTMENTS, width="medium"
            ),
            "task_title": st.column_config.TextColumn("Công việc được giao", width="large"),
            "workflow_step": st.column_config.SelectboxColumn(
                "Bước quy trình", options=WORKFLOW_STEPS, width="medium"
            ),
            "priority": st.column_config.SelectboxColumn(
                "Ưu tiên", options=["Khẩn cấp", "Cao", "Trung bình", "Thấp"], width="small"
            ),
            "status": st.column_config.SelectboxColumn(
                "Trạng thái",
                options=["Chưa bắt đầu", "Đang thực hiện", "Chờ duyệt HITL", "Hoàn thành", "Quá hạn"],
                width="small",
            ),
            "progress": st.column_config.ProgressColumn(
                "Tiến độ (%)", min_value=0, max_value=100, format="%d%%", width="small"
            ),
            "deadline": st.column_config.TextColumn("Hạn hoàn thành", width="small"),
            "kpi_quality": st.column_config.NumberColumn(
                "Điểm chất lượng (0-100)", min_value=0, max_value=100, step=1, width="small"
            ),
        },
        use_container_width=True,
        hide_index=True,
        key="tasks_table_editor",
    )

    if st.button("💾 Cập nhật Tiến độ Công việc", type="primary"):
        updated_map = {row["task_id"]: row.to_dict() for _, row in edited_tasks_df.iterrows()}
        for i, t in enumerate(st.session_state.tasks):
            if t["task_id"] in updated_map:
                st.session_state.tasks[i] = updated_map[t["task_id"]]
        st.success("Đã lưu tiến độ và trạng thái công việc!")
        st.rerun()

# ------------------------------------------
# TAB 3: ĐÁNH GIÁ KPI & BIỂU ĐỒ PHÂN TÍCH
# ------------------------------------------
with tab3:
    st.subheader("📊 Bảng Đánh giá KPI 20 Thành viên & Phân tích Hiệu suất")
    st.caption(
        "Chỉnh sửa trực tiếp số lượng ca được giao, số ca hoàn thành, tỷ lệ bác sĩ đồng thuận và SLA để hệ thống tự động tính điểm KPI và xếp loại."
    )

    kpi_edit_cols = [
        "id",
        "name",
        "department",
        "tasks_assigned",
        "tasks_completed",
        "acceptance_rate",
        "sla_compliance",
        "adr_or_initiatives",
    ]
    df_kpi_input = pd.DataFrame(st.session_state.members)[kpi_edit_cols]

    edited_kpi_input = st.data_editor(
        df_kpi_input,
        column_config={
            "id": st.column_config.TextColumn("Mã số", disabled=True, width="small"),
            "name": st.column_config.TextColumn("Họ và tên", disabled=True, width="medium"),
            "department": st.column_config.TextColumn("Khoa Lâm sàng", disabled=True, width="medium"),
            "tasks_assigned": st.column_config.NumberColumn(
                "Định mức Ca/CV giao", min_value=1, max_value=1000, step=5
            ),
            "tasks_completed": st.column_config.NumberColumn(
                "Số Ca/CV hoàn thành", min_value=0, max_value=1000, step=5
            ),
            "acceptance_rate": st.column_config.NumberColumn(
                "Tỷ lệ BS đồng thuận (%)", min_value=0.0, max_value=100.0, step=0.5, format="%.1f%%"
            ),
            "sla_compliance": st.column_config.NumberColumn(
                "Đúng hạn SLA (%)", min_value=0.0, max_value=100.0, step=0.5, format="%.1f%%"
            ),
            "adr_or_initiatives": st.column_config.NumberColumn(
                "Báo cáo ADR / Sáng kiến", min_value=0, max_value=100, step=1
            ),
        },
        use_container_width=True,
        hide_index=True,
        key="kpi_metrics_editor",
    )

    if st.button("🔄 Tính lại & Lưu Điểm KPI", type="primary"):
        for idx, row in edited_kpi_input.iterrows():
            st.session_state.members[idx]["tasks_assigned"] = int(row["tasks_assigned"])
            st.session_state.members[idx]["tasks_completed"] = int(row["tasks_completed"])
            st.session_state.members[idx]["acceptance_rate"] = float(row["acceptance_rate"])
            st.session_state.members[idx]["sla_compliance"] = float(row["sla_compliance"])
            st.session_state.members[idx]["adr_or_initiatives"] = int(row["adr_or_initiatives"])
        st.success("Đã cập nhật bảng điểm KPI toàn tổ!")
        st.rerun()

    st.markdown("#### 🏆 Bảng Xếp hạng KPI Tổng hợp")
    display_kpi_df = df_filtered[
        [
            "id",
            "name",
            "code_role",
            "department",
            "progress_score",
            "acceptance_rate",
            "sla_compliance",
            "kpi_total",
            "kpi_rank",
        ]
    ].sort_values(by="kpi_total", ascending=False)

    st.dataframe(
        display_kpi_df,
        column_config={
            "id": "Mã TV",
            "name": "Thành viên",
            "code_role": "Vai trò chuyên môn",
            "department": "Khoa Lâm sàng",
            "progress_score": st.column_config.ProgressColumn(
                "Điểm Tiến độ", min_value=0, max_value=100, format="%.1f"
            ),
            "acceptance_rate": st.column_config.NumberColumn("BS Chấp thuận (%)", format="%.1f%%"),
            "sla_compliance": st.column_config.NumberColumn("Tuân thủ SLA (%)", format="%.1f%%"),
            "kpi_total": st.column_config.ProgressColumn(
                "Tổng điểm KPI", min_value=0, max_value=100, format="%.1f"
            ),
            "kpi_rank": "Xếp loại KPI",
        },
        use_container_width=True,
        hide_index=True,
    )

    csv_kpi = display_kpi_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "📥 Xuất Bảng Xếp hạng KPI ra CSV (Excel)",
        data=csv_kpi,
        file_name="bang_danh_gia_kpi_duoc_lam_sang.csv",
        mime="text/csv",
    )

    # Biểu đồ trực quan tích hợp sẵn của Streamlit (không cần cài thêm thư viện ngoài)
    ch_col1, ch_col2 = st.columns(2)
    with ch_col1:
        st.markdown("##### 📈 Biểu đồ Điểm KPI Tổng hợp theo Thành viên")
        chart_kpi_df = display_kpi_df.set_index("name")[["kpi_total", "progress_score", "acceptance_rate"]]
        chart_kpi_df.columns = ["Tổng điểm KPI", "Điểm Tiến độ", "Tỷ lệ BS Chấp thuận"]
        st.bar_chart(chart_kpi_df, height=480)

    with ch_col2:
        st.markdown("##### 📊 Khối lượng Công việc Giao & Hoàn thành theo 5 Phân hệ")
        sub_summary = (
            df_filtered.groupby("subsystem", as_index=True)
            .agg(
                Đã_hoàn_thành=("tasks_completed", "sum"),
                Định_mức_giao=("tasks_assigned", "sum"),
            )
            .round(1)
        )
        st.bar_chart(sub_summary, height=480)

# ------------------------------------------
# TAB 4: QUY TRÌNH PHỐI HỢP 5 BƯỚC & KIẾN TRÚC
# ------------------------------------------
with tab4:
    st.subheader("🔄 Quy trình Phối hợp Luồng Công việc 5 Bước (Chuẩn Nghị định 131/2020/NĐ-CP)")
    st.markdown(
        """
1. **Bước 1 — Tiếp nhận & Phân tích ban đầu (`#01`, `#03`):** Tiếp nhận yêu cầu từ bệnh án điện tử (EMR/HIS), bác sĩ hoặc bệnh nhân ➔ `#01` phân rã tác vụ ➔ `#03` đối soát tiền sử dùng thuốc (MedRec) ➔ Chuyển dữ liệu chuẩn hóa cho các thành viên chuyên khoa.
2. **Bước 2 — Rà soát An toàn & Chuyên khoa song song (`#04` đến `#12`):** Các thành viên phân tích đồng thời: `#04` rà soát tương tác thuốc, `#05` tính eGFR/CrCl & Child-Pugh chỉnh liều thận/gan, `#06` kiểm tra đối tượng đặc biệt (thai kỳ, nhi, lão khoa), `#07-#12` hội chẩn kháng sinh ASP, giám sát TDM, tim mạch - nội tiết, hồi sức cấp cứu ICU, ung bướu và quản lý đau.
3. **Bước 3 — Tổng hợp & Kiểm duyệt Quy chuẩn (`#01`, `#02`, `#17`, `#18`):** `#01` thu thập kết quả ➔ `#18` phân tích chi phí - hiệu quả ➔ `#17` rà soát điều kiện thanh toán BHYT (Thông tư 20/2022/TT-BYT) ➔ `#02` kiểm duyệt tính pháp lý và đạo đức lâm sàng.
4. **Bước 4 — Thẩm định chuyên môn bởi Dược sĩ (Human-in-the-Loop - HITL):** Dược sĩ lâm sàng phụ trách khoa xem xét các khuyến nghị đã xếp hạng mức độ ưu tiên, phê duyệt cuối cùng và ký số gửi Bác sĩ điều trị.
5. **Bước 5 — Truyền thông, Đào tạo & Theo dõi hậu lâm sàng (`#13` đến `#16`, `#19`, `#20`):** `#15` hướng dẫn sử dụng thuốc cho người bệnh ➔ `#16` theo dõi tuân thủ điều trị (MMAS-8) ➔ `#14` báo cáo ADR theo thang Naranjo ➔ `#13`, `#19`, `#20` cập nhật Dược thư, thực hiện đánh giá sử dụng thuốc (DUE/DUR) và đào tạo CME.
"""
    )

    step_df = (
        pd.DataFrame(st.session_state.tasks)
        .groupby("workflow_step", as_index=False)
        .agg(
            so_cong_viec=("task_id", "count"),
            tien_do_tb=("progress", "mean"),
            chat_luong_tb=("kpi_quality", "mean"),
        )
        .round(1)
    )
    st.dataframe(
        step_df,
        column_config={
            "workflow_step": "Bước quy trình phối hợp",
            "so_cong_viec": "Số đầu việc đang chạy",
            "tien_do_tb": st.column_config.ProgressColumn(
                "Tiến độ TB (%)", min_value=0, max_value=100, format="%.1f%%"
            ),
            "chat_luong_tb": st.column_config.NumberColumn("Điểm chất lượng TB", format="%.1f/100"),
        },
        use_container_width=True,
        hide_index=True,
    )
