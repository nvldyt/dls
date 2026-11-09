import json
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Hệ thống Quản trị & Chấm điểm KPI Đa Module - Tổ Dược Lâm Sàng 20 Người",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

STATE_VERSION = "v3.0_modular_architecture"
WEEKDAYS = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6"]

# ==============================================================================
# DANH MỤC CHUẨN: KHOA LÂM SÀNG, PHÂN HỆ & NHÓM TÍNH CÁCH
# ==============================================================================
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

PERSONALITY_TAGS = [
    "Quyết đoán - Tư duy Điều phối Hệ thống",
    "Nguyên tắc - Kiểm soát Pháp lý & Quy chuẩn",
    "Chính xác Số liệu - Dược động học & Chỉnh liều",
    "Nhạy bén - Phản ứng Nhanh Lâm sàng & Cảnh báo",
    "Thấu cảm - Giao tiếp & Tư vấn Người bệnh",
    "Tỉ mỉ - Phân tích Dữ liệu & Nghiên cứu Học thuật",
]

# Ma trận định mức chuẩn cơ sở (Base Weekly Targets) theo từng Khoa Lâm sàng
DEPARTMENT_WORKLOAD_PROFILE = {
    "Ban Giám đốc & Phòng KHTH (Điều phối chung)": {
        "hsba_week": 50,
        "rx_out_day": 15,
        "rx_in_day": 30,
        "consult_week": 15,
        "dose_week": 15,
        "rx_total_day": 50,
        "counsel_target_pct": 80.0,
        "focus_task": "Điều phối hội chẩn liên khoa, rà soát hồ sơ bệnh án nặng và kiểm duyệt phiếu tư vấn DLS toàn viện",
    },
    "Khoa Khám bệnh & Điều trị Ngoại trú": {
        "hsba_week": 60,
        "rx_out_day": 65,
        "rx_in_day": 10,
        "consult_week": 10,
        "dose_week": 15,
        "rx_total_day": 85,
        "counsel_target_pct": 85.0,
        "focus_task": "Duyệt đơn thuốc ngoại trú, đối soát tiền sử dùng thuốc (MedRec) và tư vấn trực tiếp cách dùng thuốc cho người bệnh",
    },
    "Khoa Hồi sức tích cực - Chống độc (ICU)": {
        "hsba_week": 65,
        "rx_out_day": 5,
        "rx_in_day": 40,
        "consult_week": 25,
        "dose_week": 30,
        "rx_total_day": 50,
        "counsel_target_pct": 75.0,
        "focus_task": "Đi buồng ICU hàng ngày, giám sát nồng độ thuốc TDM (Vancomycin/Aminoglycosid), chỉnh liều lọc máu CRRT và tra cứu tương kỵ chữ Y",
    },
    "Khoa Nội Tim mạch - Lão học": {
        "hsba_week": 75,
        "rx_out_day": 30,
        "rx_in_day": 35,
        "consult_week": 15,
        "dose_week": 20,
        "rx_total_day": 75,
        "counsel_target_pct": 82.0,
        "focus_task": "Tối ưu phác đồ suy tim, tăng huyết áp, kiểm soát liều chống đông NOAC/VKA và sàng lọc tiêu chuẩn Beers lão khoa",
    },
    "Khoa Nội tiết - Đái tháo đường": {
        "hsba_week": 65,
        "rx_out_day": 45,
        "rx_in_day": 25,
        "consult_week": 12,
        "dose_week": 18,
        "rx_total_day": 80,
        "counsel_target_pct": 88.0,
        "focus_task": "Rà soát phác đồ Insulin/thuốc hạ đường huyết, tư vấn kỹ thuật tiêm Insulin và theo dõi tuân thủ điều trị MMAS-8",
    },
    "Khoa Bệnh nhiệt đới & Truyền nhiễm": {
        "hsba_week": 85,
        "rx_out_day": 15,
        "rx_in_day": 45,
        "consult_week": 25,
        "dose_week": 25,
        "rx_total_day": 68,
        "counsel_target_pct": 78.0,
        "focus_task": "Quản lý sử dụng kháng sinh (ASP), duyệt kháng sinh dự trữ, hội chẩn kháng sinh đồ và tư vấn xuống thang kháng sinh",
    },
    "Khoa Thận - Tiết niệu & Lọc máu": {
        "hsba_week": 70,
        "rx_out_day": 20,
        "rx_in_day": 35,
        "consult_week": 18,
        "dose_week": 30,
        "rx_total_day": 62,
        "counsel_target_pct": 80.0,
        "focus_task": "Tính toán eGFR/CrCl (Cockcroft-Gault) hàng ngày và can thiệp hiệu chỉnh liều thuốc cho bệnh nhân suy thận/lọc máu chu kỳ",
    },
    "Khoa Nội Hô hấp - Tiêu hóa": {
        "hsba_week": 80,
        "rx_out_day": 30,
        "rx_in_day": 35,
        "consult_week": 15,
        "dose_week": 20,
        "rx_total_day": 72,
        "counsel_target_pct": 82.0,
        "focus_task": "Rà soát tương tác thuốc chống chỉ định, chỉnh liều theo Child-Pugh và hướng dẫn sử dụng bình hít/xịt chuẩn xác",
    },
    "Khoa Sản - Phụ khoa": {
        "hsba_week": 65,
        "rx_out_day": 30,
        "rx_in_day": 30,
        "consult_week": 15,
        "dose_week": 18,
        "rx_total_day": 68,
        "counsel_target_pct": 85.0,
        "focus_task": "Thẩm định an toàn thuốc cho phụ nữ mang thai và cho con bú theo phân loại FDA/TGA, tư vấn dùng thuốc an toàn",
    },
    "Khoa Nhi tổng hợp": {
        "hsba_week": 70,
        "rx_out_day": 35,
        "rx_in_day": 30,
        "consult_week": 15,
        "dose_week": 25,
        "rx_total_day": 72,
        "counsel_target_pct": 85.0,
        "focus_task": "Kiểm tra và hiệu chỉnh liều nhi khoa theo cân nặng/diện tích da (BSA), tư vấn dạng bào chế cho trẻ em",
    },
    "Khoa Ung bướu & Huyết học lâm sàng": {
        "hsba_week": 60,
        "rx_out_day": 15,
        "rx_in_day": 35,
        "consult_week": 20,
        "dose_week": 25,
        "rx_total_day": 56,
        "counsel_target_pct": 80.0,
        "focus_task": "Kiểm tra chéo liều hóa chất theo diện tích cơ thể (BSA), dự phòng nôn CINV và xử trí sốt giảm bạch cầu hạt (ANC)",
    },
    "Khoa Phẫu thuật - Gây mê hồi sức": {
        "hsba_week": 65,
        "rx_out_day": 10,
        "rx_in_day": 40,
        "consult_week": 18,
        "dose_week": 22,
        "rx_total_day": 55,
        "counsel_target_pct": 75.0,
        "focus_task": "Giám sát kháng sinh dự phòng phẫu thuật, tối ưu thuốc giảm đau đa mô thức và dịch truyền chu phẫu",
    },
    "Khoa Ngoại Tổng hợp & Chấn thương": {
        "hsba_week": 70,
        "rx_out_day": 20,
        "rx_in_day": 35,
        "consult_week": 14,
        "dose_week": 18,
        "rx_total_day": 62,
        "counsel_target_pct": 78.0,
        "focus_task": "Kiểm soát thời gian dùng kháng sinh dự phòng và điều trị sau mổ, dự phòng huyết khối tĩnh mạch sâu",
    },
    "Khoa Thần kinh - Cơ xương khớp": {
        "hsba_week": 65,
        "rx_out_day": 30,
        "rx_in_day": 30,
        "consult_week": 14,
        "dose_week": 18,
        "rx_total_day": 68,
        "counsel_target_pct": 82.0,
        "focus_task": "Giám sát thuốc chống động kinh, dự phòng đột quỵ và kiểm soát biến cố tiêu hóa/tim mạch do NSAID",
    },
    "Đơn vị Quản lý Đau & Chăm sóc giảm nhẹ": {
        "hsba_week": 55,
        "rx_out_day": 20,
        "rx_in_day": 25,
        "consult_week": 15,
        "dose_week": 20,
        "rx_total_day": 52,
        "counsel_target_pct": 85.0,
        "focus_task": "Đánh giá thang điểm đau VAS/NPRS, tính chuyển đổi liều tương đương Opioid (MME) và dự phòng tác dụng phụ",
    },
    "Trung tâm Thông tin thuốc & Cảnh giác Dược (DI & ADR)": {
        "hsba_week": 55,
        "rx_out_day": 20,
        "rx_in_day": 25,
        "consult_week": 18,
        "dose_week": 15,
        "rx_total_day": 52,
        "counsel_target_pct": 82.0,
        "focus_task": "Tra cứu Dược thư Quốc gia/Guideline trả lời câu hỏi thông tin thuốc và thẩm định báo cáo ADR theo thang Naranjo",
    },
    "Phòng Bảo hiểm Y tế & Kinh tế Dược": {
        "hsba_week": 85,
        "rx_out_day": 45,
        "rx_in_day": 35,
        "consult_week": 12,
        "dose_week": 15,
        "rx_total_day": 90,
        "counsel_target_pct": 78.0,
        "focus_task": "Kiểm soát điều kiện thanh toán BHYT theo Thông tư 20/2022/TT-BYT, phân tích chi phí - hiệu quả và tối ưu thuốc Generic",
    },
    "Trung tâm Đào tạo & Nghiên cứu Khoa học": {
        "hsba_week": 65,
        "rx_out_day": 15,
        "rx_in_day": 25,
        "consult_week": 14,
        "dose_week": 15,
        "rx_total_day": 48,
        "counsel_target_pct": 80.0,
        "focus_task": "Thực hiện đánh giá sử dụng thuốc (DUE/DUR) toàn viện, kiểm toán đơn thuốc và biên soạn ca lâm sàng tập huấn CME",
    },
}

# Hệ số điều chỉnh chỉ tiêu theo Nhóm Tính cách
PERSONALITY_MODIFIERS = {
    "Quyết đoán - Tư duy Điều phối Hệ thống": {
        "hsba": 1.00,
        "rx": 1.00,
        "consult": 1.20,
        "dose": 1.05,
        "counsel": 1.00,
        "style_note": "Đóng vai trò chủ trì điều phối hội chẩn, kết nối nhanh bác sĩ các khoa",
    },
    "Nguyên tắc - Kiểm soát Pháp lý & Quy chuẩn": {
        "hsba": 1.15,
        "rx": 1.10,
        "consult": 0.95,
        "dose": 1.00,
        "counsel": 1.00,
        "style_note": "Tập trung rà soát chặt chẽ hồ sơ bệnh án, điều kiện BHYT và tuân thủ phác đồ Bộ Y tế",
    },
    "Chính xác Số liệu - Dược động học & Chỉnh liều": {
        "hsba": 1.05,
        "rx": 1.00,
        "consult": 1.10,
        "dose": 1.25,
        "counsel": 0.95,
        "style_note": "Chuyên sâu tính toán eGFR/CrCl, Child-Pugh, BSA và hiệu chỉnh liều TDM chuẩn xác",
    },
    "Nhạy bén - Phản ứng Nhanh Lâm sàng & Cảnh báo": {
        "hsba": 1.00,
        "rx": 1.10,
        "consult": 1.15,
        "dose": 1.15,
        "counsel": 1.00,
        "style_note": "Phát hiện tức thì tương tác thuốc nguy hiểm, cảnh báo đỏ và xử trí tình huống cấp cứu",
    },
    "Thấu cảm - Giao tiếp & Tư vấn Người bệnh": {
        "hsba": 0.95,
        "rx": 1.10,
        "consult": 0.95,
        "dose": 0.95,
        "counsel": 1.08,
        "style_note": "Ưu tiên tư vấn trực tiếp cho người bệnh, hướng dẫn kỹ thuật dùng thuốc và theo dõi tuân thủ",
    },
    "Tỉ mỉ - Phân tích Dữ liệu & Nghiên cứu Học thuật": {
        "hsba": 1.10,
        "rx": 0.95,
        "consult": 1.05,
        "dose": 1.00,
        "counsel": 1.00,
        "style_note": "Đi sâu phân tích dữ liệu DUE/DUR, thẩm định báo cáo ADR và tổng hợp y văn thực chứng",
    },
}


# ==============================================================================
# MODULE 1: DỮ LIỆU GỐC 20 THÀNH VIÊN (NHÂN SỰ, TÍNH CÁCH, NĂNG LỰC, KHOA)
# ==============================================================================
def get_default_members():
    return [
        {
            "id": "#01",
            "name": "DSCKII. Nguyễn Minh Quân",
            "code_role": "Chief Orchestrator (Tổng Điều phối DLS)",
            "subsystem": SUBSYSTEMS[0],
            "department": "Ban Giám đốc & Phòng KHTH (Điều phối chung)",
            "personality_tag": PERSONALITY_TAGS[0],
            "personality": "Quyết đoán, tư duy hệ thống, điềm tĩnh, giao tiếp đa chuyên khoa sắc bén",
            "competencies": "Điều phối luồng EMR/HIS, phân rã tác vụ hội chẩn toàn viện, tổng hợp phiếu tư vấn DLS",
            "skill_score": 96,
            "sla_compliance": 98.0,
        },
        {
            "id": "#02",
            "name": "ThS.DS. Trần Thu Hà",
            "code_role": "Clinical Compliance & Ethics (Kiểm duyệt Pháp lý Dược)",
            "subsystem": SUBSYSTEMS[0],
            "department": "Ban Giám đốc & Phòng KHTH (Điều phối chung)",
            "personality_tag": PERSONALITY_TAGS[1],
            "personality": "Nguyên tắc, cẩn trọng, tỉ mỉ, thượng tôn pháp luật và đạo đức y khoa",
            "competencies": "Kiểm soát quy chuẩn Nghị định 131/2020/NĐ-CP, thẩm định pháp lý khuyến nghị, bảo mật EMR",
            "skill_score": 94,
            "sla_compliance": 97.5,
        },
        {
            "id": "#03",
            "name": "DSCKI. Lê Hoàng Nam",
            "code_role": "Medication History & Reconciliation (Đối soát Tiền sử Thuốc)",
            "subsystem": SUBSYSTEMS[1],
            "department": "Khoa Khám bệnh & Điều trị Ngoại trú",
            "personality_tag": PERSONALITY_TAGS[4],
            "personality": "Kiên nhẫn, quan sát tinh tế, giao tiếp thân thiện khi khai thác tiền sử người bệnh",
            "competencies": "Đối soát thuốc (MedRec) khi nhập/chuyển viện, phát hiện trùng lặp hoạt chất, OCR đơn thuốc",
            "skill_score": 90,
            "sla_compliance": 95.0,
        },
        {
            "id": "#04",
            "name": "ThS.DS. Phạm Ngọc Ánh",
            "code_role": "Drug-Drug & Drug-Food Interaction (Rà soát Tương tác Thuốc)",
            "subsystem": SUBSYSTEMS[1],
            "department": "Khoa Nội Hô hấp - Tiêu hóa",
            "personality_tag": PERSONALITY_TAGS[3],
            "personality": "Nhạy bén, tư duy phân tích logic, phản ứng nhanh với các cảnh báo đỏ",
            "competencies": "Phân tích tương tác thuốc-thuốc & thuốc-thức ăn, phân tầng mức độ chống chỉ định, cảnh báo dị ứng",
            "skill_score": 93,
            "sla_compliance": 96.5,
        },
        {
            "id": "#05",
            "name": "DSCKI. Vũ Đức Thắng",
            "code_role": "Renal & Hepatic Dose Adjustment (Chỉnh liều Suy thận/Gan)",
            "subsystem": SUBSYSTEMS[1],
            "department": "Khoa Thận - Tiết niệu & Lọc máu",
            "personality_tag": PERSONALITY_TAGS[2],
            "personality": "Chính xác tuyệt đối với con số, cẩn thận, suy luận dược động học chặt chẽ",
            "competencies": "Tính eGFR, CrCl (Cockcroft-Gault), phân loại Child-Pugh, hiệu chỉnh liều cho bệnh nhân lọc máu/CRRT",
            "skill_score": 95,
            "sla_compliance": 96.5,
        },
        {
            "id": "#06",
            "name": "ThS.DS. Hoàng Minh Phương",
            "code_role": "Special Populations Safety (An toàn Thuốc Đối tượng Đặc biệt)",
            "subsystem": SUBSYSTEMS[1],
            "department": "Khoa Sản - Phụ khoa",
            "personality_tag": PERSONALITY_TAGS[4],
            "personality": "Chu đáo, ân cần, thấu cảm cao với bệnh nhân nhi, thai phụ và người cao tuổi",
            "competencies": "Thang an toàn thai kỳ FDA/TGA, tính liều nhi khoa theo cân nặng/BSA, bộ tiêu chuẩn Beers/STOPP-START",
            "skill_score": 91,
            "sla_compliance": 95.0,
        },
        {
            "id": "#07",
            "name": "TS.DS. Đặng Quốc Khánh",
            "code_role": "Anti-infective & Stewardship (Dược lâm sàng Kháng sinh & ASP)",
            "subsystem": SUBSYSTEMS[2],
            "department": "Khoa Bệnh nhiệt đới & Truyền nhiễm",
            "personality_tag": PERSONALITY_TAGS[0],
            "personality": "Bản lĩnh, quyết liệt bảo vệ phác đồ chuẩn, lập luận vi sinh - dược lý thuyết phục",
            "competencies": "Quản lý sử dụng kháng sinh (ASP), đọc kháng sinh đồ, tư vấn xuống thang và chuyển kháng sinh IV sang PO",
            "skill_score": 97,
            "sla_compliance": 96.0,
        },
        {
            "id": "#08",
            "name": "ThS.DS. Bùi Thanh Tùng",
            "code_role": "Therapeutic Drug Monitoring - TDM (Giám sát Nồng độ Thuốc)",
            "subsystem": SUBSYSTEMS[2],
            "department": "Khoa Hồi sức tích cực - Chống độc (ICU)",
            "personality_tag": PERSONALITY_TAGS[2],
            "personality": "Đam mê toán dược động học, tỉ mỉ, tập trung cao độ",
            "competencies": "Mô hình dược động học Bayes, hiệu chỉnh liều Vancomycin (AUC/MIC), Aminoglycosid, Phenytoin, Tacrolimus",
            "skill_score": 95,
            "sla_compliance": 96.5,
        },
        {
            "id": "#09",
            "name": "DSCKI. Ngô Thị Lan Hương",
            "code_role": "Cardiology & Endocrinology (DLS Tim mạch & Nội tiết)",
            "subsystem": SUBSYSTEMS[2],
            "department": "Khoa Nội Tim mạch - Lão học",
            "personality_tag": PERSONALITY_TAGS[4],
            "personality": "Điềm đạm, sâu sắc, kiên trì đồng hành cùng bệnh nhân bệnh mạn tính",
            "competencies": "Tối ưu phác đồ suy tim, tăng huyết áp, đái tháo đường, kiểm soát HbA1c, lipid máu và thuốc chống đông",
            "skill_score": 92,
            "sla_compliance": 95.5,
        },
        {
            "id": "#10",
            "name": "DSCKII. Trịnh Quang Huy",
            "code_role": "ICU & Emergency Critical Care (DLS Hồi sức Cấp cứu)",
            "subsystem": SUBSYSTEMS[2],
            "department": "Khoa Hồi sức tích cực - Chống độc (ICU)",
            "personality_tag": PERSONALITY_TAGS[3],
            "personality": "Bình tĩnh dưới áp lực cao, phản xạ lâm sàng tức thì, phối hợp ăn ý với bác sĩ trực",
            "competencies": "Thuốc vận mạch, an thần - giảm đau ICU, tra cứu tương kỵ truyền tĩnh mạch chữ Y (Y-site), đánh giá SOFA",
            "skill_score": 96,
            "sla_compliance": 98.5,
        },
        {
            "id": "#11",
            "name": "ThS.DS. Lý Mỹ Linh",
            "code_role": "Oncology & Supportive Care (DLS Ung bướu & Huyết học)",
            "subsystem": SUBSYSTEMS[2],
            "department": "Khoa Ung bướu & Huyết học lâm sàng",
            "personality_tag": PERSONALITY_TAGS[2],
            "personality": "Kỹ lưỡng, giàu lòng trắc ẩn, kiểm tra chéo đa tầng không để xảy ra sai sót",
            "competencies": "Kiểm duyệt liều hóa trị/nhắm trúng đích theo BSA, dự phòng nôn, xử trí sốt giảm bạch cầu hạt (ANC)",
            "skill_score": 93,
            "sla_compliance": 96.0,
        },
        {
            "id": "#12",
            "name": "DSCKI. Đỗ Văn Khôi",
            "code_role": "Pain Management & Palliative Care (Quản lý Đau & Giảm nhẹ)",
            "subsystem": SUBSYSTEMS[2],
            "department": "Đơn vị Quản lý Đau & Chăm sóc giảm nhẹ",
            "personality_tag": PERSONALITY_TAGS[4],
            "personality": "Nhẹ nhàng, lắng nghe, thấu hiểu tâm lý người bệnh đau mạn tính",
            "competencies": "Thang điểm đau VAS/NPRS, tính chuyển đổi liều tương đương Opioid (MME), dự phòng ức chế hô hấp & táo bón",
            "skill_score": 89,
            "sla_compliance": 94.0,
        },
        {
            "id": "#13",
            "name": "ThS.DS. Mai Thanh Thảo",
            "code_role": "Medical Literature & RAG Query (Tra cứu Dược thư & Phác đồ)",
            "subsystem": SUBSYSTEMS[3],
            "department": "Trung tâm Thông tin thuốc & Cảnh giác Dược (DI & ADR)",
            "personality_tag": PERSONALITY_TAGS[5],
            "personality": "Ham học hỏi, tư duy học thuật chuẩn mực, trích dẫn bằng chứng y khoa chính xác",
            "competencies": "Truy xuất Dược thư Quốc gia, Micromedex, AHFS, Hướng dẫn Bộ Y tế, tổng hợp điểm tin thông tin thuốc",
            "skill_score": 94,
            "sla_compliance": 97.5,
        },
        {
            "id": "#14",
            "name": "DSCKI. Phan Anh Tuấn",
            "code_role": "Pharmacovigilance & ADR Reporting (Cảnh giác Dược & ADR)",
            "subsystem": SUBSYSTEMS[3],
            "department": "Trung tâm Thông tin thuốc & Cảnh giác Dược (DI & ADR)",
            "personality_tag": PERSONALITY_TAGS[5],
            "personality": "Bền bỉ, tinh thần cảnh giác cao, phân tích nguyên nhân - hệ quả khách quan",
            "competencies": "Đánh giá thang Naranjo và WHO-UMC, lập báo cáo ADR gửi Trung tâm DI & ADR Quốc gia, truy vết chuỗi phản ứng",
            "skill_score": 92,
            "sla_compliance": 96.0,
        },
        {
            "id": "#15",
            "name": "DSĐH. Nguyễn Bảo Ngọc",
            "code_role": "Patient Medication Education (Tư vấn & Hướng dẫn Bệnh nhân)",
            "subsystem": SUBSYSTEMS[3],
            "department": "Khoa Khám bệnh & Điều trị Ngoại trú",
            "personality_tag": PERSONALITY_TAGS[4],
            "personality": "Hoạt ngôn, truyền cảm, biến kiến thức y khoa phức tạp thành lời khuyên dễ hiểu",
            "competencies": "Tư vấn kỹ thuật dùng bình hít/xịt COPD-Hen, bút tiêm Insulin, thời điểm dùng thuốc và chế độ dinh dưỡng",
            "skill_score": 90,
            "sla_compliance": 95.5,
        },
        {
            "id": "#16",
            "name": "DSĐH. Trương Gia Bảo",
            "code_role": "Digital Adherence & Refill Monitor (Theo dõi Tuân thủ Điều trị)",
            "subsystem": SUBSYSTEMS[3],
            "department": "Khoa Nội tiết - Đái tháo đường",
            "personality_tag": PERSONALITY_TAGS[4],
            "personality": "Nhiệt tình, kỷ luật, tận tâm đồng hành cùng bệnh nhân ngoại trú",
            "competencies": "Đánh giá tuân thủ điều trị theo thang MMAS-8, quản lý lịch nhắc uống thuốc Telehealth, cảnh báo bỏ liều",
            "skill_score": 88,
            "sla_compliance": 94.0,
        },
        {
            "id": "#17",
            "name": "DSCKI. Hà Kiều Trang",
            "code_role": "Health Insurance & Formulary Compliance (Kiểm soát BHYT)",
            "subsystem": SUBSYSTEMS[4],
            "department": "Phòng Bảo hiểm Y tế & Kinh tế Dược",
            "personality_tag": PERSONALITY_TAGS[1],
            "personality": "Sắc sảo, nắm vững thông tư, bảo vệ an toàn quỹ BHYT và quyền lợi người bệnh",
            "competencies": "Rà soát điều kiện thanh toán BHYT theo Thông tư 20/2022/TT-BYT, phòng ngừa xuất toán thuốc ngoài danh mục",
            "skill_score": 95,
            "sla_compliance": 98.0,
        },
        {
            "id": "#18",
            "name": "ThS.DS. Lương Thế Vinh",
            "code_role": "Pharmacoeconomics & Cost-Optimization (Kinh tế Dược)",
            "subsystem": SUBSYSTEMS[4],
            "department": "Phòng Bảo hiểm Y tế & Kinh tế Dược",
            "personality_tag": PERSONALITY_TAGS[2],
            "personality": "Thực tế, tư duy tối ưu hóa nguồn lực, cân bằng hiệu quả điều trị và chi phí",
            "competencies": "Phân tích chi phí - hiệu quả (CEA), tư vấn chuyển đổi thuốc Generic/Biosimilar, phân tích ABC/VEN",
            "skill_score": 91,
            "sla_compliance": 94.5,
        },
        {
            "id": "#19",
            "name": "TS.DS. Chu Hoàng Yến",
            "code_role": "Clinical Audit & DUE/DUR (Đánh giá Sử dụng Thuốc & NCKH)",
            "subsystem": SUBSYSTEMS[4],
            "department": "Trung tâm Đào tạo & Nghiên cứu Khoa học",
            "personality_tag": PERSONALITY_TAGS[5],
            "personality": "Tư duy dữ liệu lớn, sắc bén trong nghiên cứu khoa học và cải tiến chất lượng",
            "competencies": "Thiết kế đề cương DUE/DUR, thống kê y sinh, kiểm toán đơn thuốc toàn viện, viết báo cáo NCKH",
            "skill_score": 94,
            "sla_compliance": 96.5,
        },
        {
            "id": "#20",
            "name": "ThS.DS. Nguyễn Xuân Bách",
            "code_role": "Pharmacist Continuing Education - CME (Đào tạo Liên tục)",
            "subsystem": SUBSYSTEMS[4],
            "department": "Trung tâm Đào tạo & Nghiên cứu Khoa học",
            "personality_tag": PERSONALITY_TAGS[5],
            "personality": "Truyền cảm hứng, sáng tạo, luôn cập nhật xu hướng y học thực chứng mới nhất",
            "competencies": "Xây dựng ngân hàng ca lâm sàng (Case Study), tổ chức sinh hoạt khoa học CME, cập nhật PubMed/Guideline",
            "skill_score": 91,
            "sla_compliance": 95.0,
        },
    ]


# ==============================================================================
# MODULE 2: ENGINE TỰ ĐỘNG PHÂN CÔNG CÔNG VIỆC & CHỈ TIÊU HÀNG TUẦN
# ==============================================================================
def auto_assign_weekly_plan_for_member(member, workload_scale=1.0):
    """
    Tự động tính toán định mức mục tiêu tuần (Thứ 2 - Thứ 6) và phân công công việc
    dựa trên: (1) Khoa lâm sàng phụ trách, (2) Nhóm tính cách, (3) Điểm năng lực (skill_score).
    """
    dept = member.get("department", CLINICAL_DEPARTMENTS[0])
    p_tag = member.get("personality_tag", PERSONALITY_TAGS[0])
    skill = float(member.get("skill_score", 90))

    base_prof = DEPARTMENT_WORKLOAD_PROFILE.get(
        dept, DEPARTMENT_WORKLOAD_PROFILE[CLINICAL_DEPARTMENTS[0]]
    )
    p_mod = PERSONALITY_MODIFIERS.get(p_tag, PERSONALITY_MODIFIERS[PERSONALITY_TAGS[0]])

    # Hệ số năng lực cá nhân (chuẩn 90 điểm = 1.0)
    skill_factor = max(0.75, min(1.25, skill / 90.0)) * float(workload_scale)

    hsba_target_week = max(15, int(round(base_prof["hsba_week"] * p_mod["hsba"] * skill_factor / 5.0) * 5))
    rx_out_target_week = max(10, int(round(base_prof["rx_out_day"] * 5 * p_mod["rx"] * skill_factor / 5.0) * 5))
    rx_in_target_week = max(10, int(round(base_prof["rx_in_day"] * 5 * p_mod["rx"] * skill_factor / 5.0) * 5))
    consult_target_week = max(5, int(round(base_prof["consult_week"] * p_mod["consult"] * skill_factor)))
    dose_target_week = max(5, int(round(base_prof["dose_week"] * p_mod["dose"] * skill_factor)))
    rx_total_week_est = max(
        rx_out_target_week + rx_in_target_week + 25,
        int(round(base_prof["rx_total_day"] * 5 * skill_factor)),
    )
    counsel_target_pct = round(min(98.0, max(65.0, base_prof["counsel_target_pct"] * p_mod["counsel"])), 1)

    assigned_task_desc = (
        f"[{dept}] {base_prof['focus_task']} | "
        f"Phát huy thế mạnh ({p_tag}): {p_mod['style_note']}."
    )

    return {
        "member_id": member["id"],
        "member_name": member["name"],
        "department": dept,
        "personality_tag": p_tag,
        "skill_score": int(skill),
        "assigned_task": assigned_task_desc,
        "hsba_target_week": hsba_target_week,
        "rx_out_target_week": rx_out_target_week,
        "rx_in_target_week": rx_in_target_week,
        "consult_target_week": consult_target_week,
        "dose_target_week": dose_target_week,
        "rx_total_week_est": rx_total_week_est,
        "counsel_target_pct": counsel_target_pct,
        "assignment_completion_pct": 96.0 if skill >= 93 else 92.0,
    }


def generate_all_modules_from_auto_assignment(members_list, workload_scale=1.0):
    """Khởi tạo đồng bộ dữ liệu cho Module 2, 3, 4, 5, 6, 7 từ thuật toán phân công tự động."""
    m2_assignments = []
    m3_hsba = []
    m4_rx = []
    m5_consult = []
    m6_dose = []
    m7_counsel = []

    for idx, m in enumerate(members_list):
        plan = auto_assign_weekly_plan_for_member(m, workload_scale=workload_scale)
        m2_assignments.append(plan)

        # --- Module 3: Kiểm tra HSBA từ Thứ 2 đến Thứ 6 ---
        base_hsba_d = plan["hsba_target_week"] // 5
        m3_hsba.append(
            {
                "member_id": m["id"],
                "member_name": m["name"],
                "department": m["department"],
                "target_week": plan["hsba_target_week"],
                "Thứ 2": base_hsba_d + (1 if idx % 3 == 0 else 0),
                "Thứ 3": base_hsba_d,
                "Thứ 4": base_hsba_d + (1 if idx % 2 == 0 else -1),
                "Thứ 5": base_hsba_d,
                "Thứ 6": base_hsba_d + (1 if idx % 4 == 0 else 0),
            }
        )

        # --- Module 4: Duyệt Đơn Ngoại trú & Nội trú (Thứ 2 - Thứ 6) ---
        out_d = plan["rx_out_target_week"] // 5
        in_d = plan["rx_in_target_week"] // 5
        m4_rx.append(
            {
                "member_id": m["id"],
                "member_name": m["name"],
                "department": m["department"],
                "target_out_week": plan["rx_out_target_week"],
                "target_in_week": plan["rx_in_target_week"],
                "out_t2": out_d,
                "out_t3": out_d + 2,
                "out_t4": out_d - 1,
                "out_t5": out_d + 1,
                "out_t6": out_d,
                "in_t2": in_d,
                "in_t3": in_d + 1,
                "in_t4": in_d,
                "in_t5": in_d + 1,
                "in_t6": in_d - 1,
            }
        )

        # --- Module 5: Hội chẩn Lâm sàng Hàng ngày (Thứ 2 - Thứ 6) ---
        con_d = max(1, plan["consult_target_week"] // 5)
        m5_consult.append(
            {
                "member_id": m["id"],
                "member_name": m["name"],
                "department": m["department"],
                "target_consult_week": plan["consult_target_week"],
                "Thứ 2": con_d,
                "Thứ 3": con_d + (1 if idx % 2 == 0 else 0),
                "Thứ 4": con_d,
                "Thứ 5": con_d + (1 if idx % 3 == 0 else 0),
                "Thứ 6": con_d,
                "doctor_consensus_pct": round(93.0 + (idx % 6) * 1.0, 1),
            }
        )

        # --- Module 6: Can thiệp Chỉnh liều Lâm sàng Hàng ngày (Thứ 2 - Thứ 6) ---
        dose_d = max(1, plan["dose_target_week"] // 5)
        m6_dose.append(
            {
                "member_id": m["id"],
                "member_name": m["name"],
                "department": m["department"],
                "target_dose_week": plan["dose_target_week"],
                "Thứ 2": dose_d,
                "Thứ 3": dose_d + 1,
                "Thứ 4": dose_d,
                "Thứ 5": dose_d + (1 if idx % 2 == 1 else 0),
                "Thứ 6": dose_d,
                "intervention_success_pct": round(94.0 + (idx % 5) * 1.0, 1),
            }
        )

        # --- Module 7: Tư vấn Đơn thuốc / Tổng số Đơn trong Ngày (Thứ 2 - Thứ 6) ---
        tot_d = max(10, plan["rx_total_week_est"] // 5)
        coun_d = min(tot_d, int(round(tot_d * (plan["counsel_target_pct"] / 100.0))))
        m7_counsel.append(
            {
                "member_id": m["id"],
                "member_name": m["name"],
                "department": m["department"],
                "target_counsel_pct": plan["counsel_target_pct"],
                "coun_t2": coun_d,
                "tot_t2": tot_d,
                "coun_t3": min(tot_d + 2, coun_d + 2),
                "tot_t3": tot_d + 2,
                "coun_t4": coun_d,
                "tot_t4": tot_d,
                "coun_t5": min(tot_d + 1, coun_d + 1),
                "tot_t5": tot_d + 1,
                "coun_t6": coun_d,
                "tot_t6": tot_d,
            }
        )

    return m2_assignments, m3_hsba, m4_rx, m5_consult, m6_dose, m7_counsel


# ==============================================================================
# CÁC HÀM CHẤM ĐIỂM ĐỘC LẬP CHO TỪNG MODULE TIÊU CHÍ (THANG ĐIỂM 0 - 100)
# ==============================================================================
def score_module_3_hsba(m3_list):
    df = pd.DataFrame(m3_list).copy()
    for d in WEEKDAYS:
        df[d] = pd.to_numeric(df[d], errors="coerce").fillna(0).astype(int)
    df["target_week"] = pd.to_numeric(df["target_week"], errors="coerce").fillna(1).clip(lower=1).astype(int)
    df["done_week"] = df[WEEKDAYS].sum(axis=1)
    df["diff_week"] = df["done_week"] - df["target_week"]
    df["completion_pct"] = ((df["done_week"] / df["target_week"]) * 100.0).round(1)
    # Điểm chấm tiêu chí 1 (tối đa 100 điểm)
    df["score_m3"] = df["completion_pct"].clip(0.0, 100.0).round(1)
    return df


def score_module_4_prescription(m4_list):
    df = pd.DataFrame(m4_list).copy()
    out_cols = ["out_t2", "out_t3", "out_t4", "out_t5", "out_t6"]
    in_cols = ["in_t2", "in_t3", "in_t4", "in_t5", "in_t6"]
    for c in out_cols + in_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    df["target_out_week"] = pd.to_numeric(df["target_out_week"], errors="coerce").fillna(1).clip(lower=1).astype(int)
    df["target_in_week"] = pd.to_numeric(df["target_in_week"], errors="coerce").fillna(1).clip(lower=1).astype(int)

    df["done_out_week"] = df[out_cols].sum(axis=1)
    df["done_in_week"] = df[in_cols].sum(axis=1)
    df["done_total_rx"] = df["done_out_week"] + df["done_in_week"]
    df["target_total_rx"] = df["target_out_week"] + df["target_in_week"]

    df["out_pct"] = ((df["done_out_week"] / df["target_out_week"]) * 100.0).clip(0.0, 110.0).round(1)
    df["in_pct"] = ((df["done_in_week"] / df["target_in_week"]) * 100.0).clip(0.0, 110.0).round(1)
    # Điểm chấm tiêu chí 2: kết hợp tỷ lệ hoàn thành tổng đơn duyệt (50%) + cân đối ngoại/nội trú (50%)
    total_pct = ((df["done_total_rx"] / df["target_total_rx"].replace(0, 1)) * 100.0).clip(0.0, 100.0)
    balance_pct = (0.5 * df["out_pct"].clip(0.0, 100.0) + 0.5 * df["in_pct"].clip(0.0, 100.0))
    df["score_m4"] = (0.5 * total_pct + 0.5 * balance_pct).round(1)
    return df


def score_module_5_consultation(m5_list):
    df = pd.DataFrame(m5_list).copy()
    for d in WEEKDAYS:
        df[d] = pd.to_numeric(df[d], errors="coerce").fillna(0).astype(int)
    df["target_consult_week"] = (
        pd.to_numeric(df["target_consult_week"], errors="coerce").fillna(1).clip(lower=1).astype(int)
    )
    df["doctor_consensus_pct"] = (
        pd.to_numeric(df["doctor_consensus_pct"], errors="coerce").fillna(90.0).clip(0.0, 100.0)
    )
    df["done_consult_week"] = df[WEEKDAYS].sum(axis=1)
    df["consult_qty_pct"] = ((df["done_consult_week"] / df["target_consult_week"]) * 100.0).clip(0.0, 110.0).round(1)
    # Điểm chấm tiêu chí 3: 65% khối lượng hội chẩn đạt mục tiêu + 35% tỷ lệ BS đồng thuận
    df["score_m5"] = (
        0.65 * df["consult_qty_pct"].clip(0.0, 100.0) + 0.35 * df["doctor_consensus_pct"]
    ).round(1)
    return df


def score_module_6_dose_intervention(m6_list):
    df = pd.DataFrame(m6_list).copy()
    for d in WEEKDAYS:
        df[d] = pd.to_numeric(df[d], errors="coerce").fillna(0).astype(int)
    df["target_dose_week"] = (
        pd.to_numeric(df["target_dose_week"], errors="coerce").fillna(1).clip(lower=1).astype(int)
    )
    df["intervention_success_pct"] = (
        pd.to_numeric(df["intervention_success_pct"], errors="coerce").fillna(92.0).clip(0.0, 100.0)
    )
    df["done_dose_week"] = df[WEEKDAYS].sum(axis=1)
    df["dose_qty_pct"] = ((df["done_dose_week"] / df["target_dose_week"]) * 100.0).clip(0.0, 110.0).round(1)
    # Điểm chấm tiêu chí 4: 65% số ca chỉnh liều đạt mục tiêu + 35% tỷ lệ chỉnh liều thành công
    df["score_m6"] = (
        0.65 * df["dose_qty_pct"].clip(0.0, 100.0) + 0.35 * df["intervention_success_pct"]
    ).round(1)
    return df


def score_module_7_counseling(m7_list):
    df = pd.DataFrame(m7_list).copy()
    c_cols = ["coun_t2", "coun_t3", "coun_t4", "coun_t5", "coun_t6"]
    t_cols = ["tot_t2", "tot_t3", "tot_t4", "tot_t5", "tot_t6"]
    for c in c_cols + t_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    df["target_counsel_pct"] = (
        pd.to_numeric(df["target_counsel_pct"], errors="coerce").fillna(80.0).clip(1.0, 100.0)
    )

    df["counseled_week"] = df[c_cols].sum(axis=1)
    df["total_rx_week"] = df[t_cols].sum(axis=1).replace(0, 1)
    df["actual_counsel_pct"] = ((df["counseled_week"] / df["total_rx_week"]) * 100.0).clip(0.0, 100.0).round(1)
    # Điểm chấm tiêu chí 5: So sánh tỷ lệ tư vấn thực tế với mục tiêu tỷ lệ tư vấn
    df["score_m7"] = ((df["actual_counsel_pct"] / df["target_counsel_pct"]) * 100.0).clip(0.0, 100.0).round(1)
    return df


def compute_master_kpi_module8(members_list, m2_list, df_m3, df_m4, df_m5, df_m6, df_m7, weights):
    """
    MODULE 8: Tổng hợp toàn bộ điểm số từ các Module độc lập (Module 2, 3, 4, 5, 6, 7)
    và tính Tổng điểm KPI + Xếp loại.
    """
    df_base = pd.DataFrame(members_list)[
        ["id", "name", "code_role", "subsystem", "department", "personality_tag", "skill_score", "sla_compliance"]
    ].copy()

    df_m2 = pd.DataFrame(m2_list)[["member_id", "assigned_task", "assignment_completion_pct"]].copy()

    merged = (
        df_base.merge(df_m2, left_on="id", right_on="member_id", how="left")
        .drop(columns=["member_id"])
        .merge(df_m3[["member_id", "done_week", "target_week", "score_m3"]], left_on="id", right_on="member_id", how="left")
        .drop(columns=["member_id"])
        .merge(df_m4[["member_id", "done_out_week", "done_in_week", "done_total_rx", "score_m4"]], left_on="id", right_on="member_id", how="left")
        .drop(columns=["member_id"])
        .merge(df_m5[["member_id", "done_consult_week", "target_consult_week", "score_m5"]], left_on="id", right_on="member_id", how="left")
        .drop(columns=["member_id"])
        .merge(df_m6[["member_id", "done_dose_week", "target_dose_week", "score_m6"]], left_on="id", right_on="member_id", how="left")
        .drop(columns=["member_id"])
        .merge(df_m7[["member_id", "counseled_week", "total_rx_week", "actual_counsel_pct", "score_m7"]], left_on="id", right_on="member_id", how="left")
        .drop(columns=["member_id"])
    )

    for s_col in ["score_m3", "score_m4", "score_m5", "score_m6", "score_m7", "assignment_completion_pct"]:
        merged[s_col] = pd.to_numeric(merged[s_col], errors="coerce").fillna(90.0)

    total_w = max(sum(weights.values()), 1)
    merged["kpi_total"] = (
        (
            merged["score_m3"] * weights["w_m3_hsba"]
            + merged["score_m4"] * weights["w_m4_rx"]
            + merged["score_m5"] * weights["w_m5_consult"]
            + merged["score_m6"] * weights["w_m6_dose"]
            + merged["score_m7"] * weights["w_m7_counsel"]
            + merged["assignment_completion_pct"] * weights["w_m2_task"]
        )
        / total_w
    ).round(1)

    def rank_kpi(val):
        if val >= 95.0:
            return "Xuất sắc (A+)"
        elif val >= 90.0:
            return "Tốt (A)"
        elif val >= 80.0:
            return "Đạt chuẩn (B)"
        else:
            return "Cần cải thiện (C)"

    merged["kpi_rank"] = merged["kpi_total"].apply(rank_kpi)
    return merged


# ==============================================================================
# KHỞI TẠO AN TOÀN SESSION STATE (CHỐNG LỖI KHI CẬP NHẬT PHIÊN BẢN MỚI)
# ==============================================================================
def ensure_session_state_initialized(force_reset=False):
    if force_reset or st.session_state.get("app_version") != STATE_VERSION:
        st.session_state.app_version = STATE_VERSION
        st.session_state.members = get_default_members()
        m2, m3, m4, m5, m6, m7 = generate_all_modules_from_auto_assignment(
            st.session_state.members, workload_scale=1.0
        )
        st.session_state.m2_assignments = m2
        st.session_state.m3_hsba = m3
        st.session_state.m4_rx = m4
        st.session_state.m5_consult = m5
        st.session_state.m6_dose = m6
        st.session_state.m7_counsel = m7


ensure_session_state_initialized(force_reset=False)


# ==============================================================================
# THANH BÊN (SIDEBAR): ĐIỀU KHIỂN TRỌNG SỐ KPI & SAO LƯU HỆ THỐNG
# ==============================================================================
with st.sidebar:
    st.markdown("## 🧩 KIẾN TRÚC 8 MODULE ĐỘC LẬP")
    st.caption("Tổ Dược Lâm Sàng 20 Thành viên • Chuẩn Nghị định 131/2020/NĐ-CP")

    selected_subsystem = st.multiselect(
        "Lọc theo Phân hệ Chuyên môn",
        options=SUBSYSTEMS,
        default=SUBSYSTEMS,
    )

    st.markdown("### ⚖️ Trọng số Chấm KPI (Module 8)")
    w_m3_hsba = st.slider("1. Kiểm tra HSBA Tuần (%)", 5, 50, 25, 5)
    w_m4_rx = st.slider("2. Duyệt Đơn Ngoại & Nội trú (%)", 5, 50, 20, 5)
    w_m5_consult = st.slider("3. Hội chẩn Lâm sàng (%)", 5, 50, 15, 5)
    w_m6_dose = st.slider("4. Can thiệp Chỉnh liều (%)", 5, 50, 15, 5)
    w_m7_counsel = st.slider("5. Tư vấn Đơn / Tổng đơn (%)", 5, 50, 15, 5)
    w_m2_task = st.slider("6. Công việc Phân công Tuần (%)", 5, 50, 10, 5)

    weights_dict = {
        "w_m3_hsba": w_m3_hsba,
        "w_m4_rx": w_m4_rx,
        "w_m5_consult": w_m5_consult,
        "w_m6_dose": w_m6_dose,
        "w_m7_counsel": w_m7_counsel,
        "w_m2_task": w_m2_task,
    }
    st.caption(f"Tổng trọng số: **{sum(weights_dict.values())}%** (tự động quy chuẩn thang 100)")

    st.markdown("### 💾 Sao lưu & Khôi phục Toàn bộ Module")
    backup_payload = {
        "app_version": STATE_VERSION,
        "updated_at": datetime.now().isoformat(),
        "members": st.session_state.members,
        "m2_assignments": st.session_state.m2_assignments,
        "m3_hsba": st.session_state.m3_hsba,
        "m4_rx": st.session_state.m4_rx,
        "m5_consult": st.session_state.m5_consult,
        "m6_dose": st.session_state.m6_dose,
        "m7_counsel": st.session_state.m7_counsel,
    }
    st.download_button(
        label="⬇️ Tải xuống Toàn bộ 8 Module (JSON)",
        data=json.dumps(backup_payload, ensure_ascii=False, indent=2),
        file_name="he_thong_8_module_duoc_lam_sang.json",
        mime="application/json",
        use_container_width=True,
    )

    uploaded_file = st.file_uploader("⬆️ Nạp file cấu hình (.json)", type=["json"])
    if uploaded_file is not None:
        try:
            loaded = json.load(uploaded_file)
            if loaded.get("app_version") == STATE_VERSION:
                st.session_state.members = loaded["members"]
                st.session_state.m2_assignments = loaded["m2_assignments"]
                st.session_state.m3_hsba = loaded["m3_hsba"]
                st.session_state.m4_rx = loaded["m4_rx"]
                st.session_state.m5_consult = loaded["m5_consult"]
                st.session_state.m6_dose = loaded["m6_dose"]
                st.session_state.m7_counsel = loaded["m7_counsel"]
                st.success("Đã khôi phục toàn bộ 8 Module thành công!")
            else:
                st.warning("File JSON thuộc phiên bản cũ, hệ thống đã giữ cấu trúc 8 Module mới.")
        except Exception as exc:
            st.error(f"Lỗi đọc file JSON: {exc}")

    if st.button("🔄 Khôi phục Mặc định 8 Module", use_container_width=True):
        ensure_session_state_initialized(force_reset=True)
        st.rerun()


# ==============================================================================
# TÍNH TOÁN ĐIỂM SỐ ĐỘC LẬP CỦA TỪNG MODULE & TỔNG HỢP MODULE 8
# ==============================================================================
df_m3_scored = score_module_3_hsba(st.session_state.m3_hsba)
df_m4_scored = score_module_4_prescription(st.session_state.m4_rx)
df_m5_scored = score_module_5_consultation(st.session_state.m5_consult)
df_m6_scored = score_module_6_dose_intervention(st.session_state.m6_dose)
df_m7_scored = score_module_7_counseling(st.session_state.m7_counsel)

df_master_kpi = compute_master_kpi_module8(
    st.session_state.members,
    st.session_state.m2_assignments,
    df_m3_scored,
    df_m4_scored,
    df_m5_scored,
    df_m6_scored,
    df_m7_scored,
    weights_dict,
)

df_master_filtered = df_master_kpi[df_master_kpi["subsystem"].isin(selected_subsystem)].copy()
filtered_ids = set(df_master_filtered["id"].tolist())

# ==============================================================================
# TIÊU ĐỀ CHÍNH & BẢNG CHỈ SỐ TỔNG QUAN 6 TRỤ CỘT
# ==============================================================================
st.title("🏥 Hệ Thống Quản Trị & Chấm Điểm KPI Đa Module — Tổ Dược Lâm Sàng 20 Người")
st.markdown(
    "**Kiến trúc tách biệt độc lập từng Module tiêu chí mục tiêu (Thứ 2 – Thứ 6), Module Tự động Phân công theo Khoa - Tính cách - Năng lực & Module Tổng hợp KPI**"
)

k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1:
    st.metric(
        "M3: Bệnh án Tuần (T2–T6)",
        f"{int(df_master_filtered['done_week'].sum()):,}/{int(df_master_filtered['target_week'].sum()):,}",
        f"Điểm TB: {df_master_filtered['score_m3'].mean():.1f}/100",
    )
with k2:
    st.metric(
        "M4: Đơn Ngoại & Nội trú",
        f"{int(df_master_filtered['done_total_rx'].sum()):,} đơn",
        f"Điểm TB: {df_master_filtered['score_m4'].mean():.1f}/100",
    )
with k3:
    st.metric(
        "M5: Hội chẩn Lâm sàng",
        f"{int(df_master_filtered['done_consult_week'].sum()):,} ca",
        f"Điểm TB: {df_master_filtered['score_m5'].mean():.1f}/100",
    )
with k4:
    st.metric(
        "M6: Can thiệp Chỉnh liều",
        f"{int(df_master_filtered['done_dose_week'].sum()):,} ca",
        f"Điểm TB: {df_master_filtered['score_m6'].mean():.1f}/100",
    )
with k5:
    tot_c = int(df_master_filtered["counseled_week"].sum())
    tot_rx = max(int(df_master_filtered["total_rx_week"].sum()), 1)
    st.metric(
        "M7: Tư vấn / Tổng đơn",
        f"{tot_c:,}/{tot_rx:,} ({(tot_c/tot_rx)*100:.1f}%)",
        f"Điểm TB: {df_master_filtered['score_m7'].mean():.1f}/100",
    )
with k6:
    st.metric(
        "M8: Tổng Điểm KPI Tổ",
        f"{df_master_filtered['kpi_total'].mean():.1f} / 100",
        f"{int((df_master_filtered['kpi_rank'] == 'Xuất sắc (A+)').sum())}/20 đạt A+",
    )

# ==============================================================================
# GIAO DIỆN 8 MODULE ĐỘC LẬP (8 TABS CHUYÊN BIỆT)
# ==============================================================================
(
    tab_m1,
    tab_m2,
    tab_m3,
    tab_m4,
    tab_m5,
    tab_m6,
    tab_m7,
    tab_m8,
) = st.tabs(
    [
        "👥 Module 1: Hồ sơ Nhân sự (Khoa, Tính cách, Năng lực)",
        "🤖 Module 2: Tự động Phân công Công việc Hàng tuần",
        "📁 Module 3: Tiêu chí Hồ sơ Bệnh án (T2–T6)",
        "💊 Module 4: Tiêu chí Duyệt Đơn Ngoại & Nội trú",
        "🩺 Module 5: Tiêu chí Hội chẩn Lâm sàng",
        "⚖️ Module 6: Tiêu chí Can thiệp Chỉnh liều",
        "🗣️ Module 7: Tiêu chí Tư vấn Đơn / Tổng đơn",
        "🏆 Module 8: Tổng hợp & Tính KPI Toàn diện",
    ]
)

# ------------------------------------------------------------------------------
# MODULE 1: CÀI ĐẶT NHÂN SỰ, KHOA LÂM SÀNG, TÍNH CÁCH & NĂNG LỰC
# ------------------------------------------------------------------------------
with tab_m1:
    st.subheader("👥 Module 1: Cài đặt Khoa Lâm sàng, Nhóm Tính cách & Năng lực cho 20 Thành viên")
    st.info(
        "💡 **Vai trò của Module 1:** Khi bạn thay đổi **Khoa Lâm sàng phụ trách**, **Nhóm Tính cách** hoặc **Điểm Năng lực** tại đây, **Module 2** sẽ dựa vào dữ liệu này để tự động phân công công việc và tính toán định mức mục tiêu hàng tuần cho từng bạn."
    )

    m1_cols = [
        "id",
        "name",
        "code_role",
        "subsystem",
        "department",
        "personality_tag",
        "skill_score",
        "personality",
        "competencies",
    ]
    edited_m1 = st.data_editor(
        pd.DataFrame(st.session_state.members)[m1_cols],
        column_config={
            "id": st.column_config.TextColumn("Mã TV", disabled=True, width="small"),
            "name": st.column_config.TextColumn("Họ và tên Dược sĩ", width="medium"),
            "code_role": st.column_config.TextColumn("Chức danh chuyên môn", width="medium"),
            "subsystem": st.column_config.SelectboxColumn("Phân hệ", options=SUBSYSTEMS, width="medium"),
            "department": st.column_config.SelectboxColumn(
                "Khoa Lâm sàng phụ trách", options=CLINICAL_DEPARTMENTS, width="medium"
            ),
            "personality_tag": st.column_config.SelectboxColumn(
                "Nhóm Tính cách Chủ đạo", options=PERSONALITY_TAGS, width="medium"
            ),
            "skill_score": st.column_config.NumberColumn(
                "Điểm Năng lực (50-100)", min_value=50, max_value=100, step=1, width="small"
            ),
            "personality": st.column_config.TextColumn("Mô tả Tính cách chi tiết", width="large"),
            "competencies": st.column_config.TextColumn("Năng lực chuyên môn & Công cụ", width="large"),
        },
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        key="editor_module_1",
    )

    c_save_m1, c_sync_m1 = st.columns(2)
    with c_save_m1:
        if st.button("💾 Lưu Hồ sơ Nhân sự (Module 1)", type="primary", use_container_width=True):
            for idx, row in edited_m1.iterrows():
                for col in m1_cols:
                    st.session_state.members[idx][col] = row[col]
                # Đồng bộ tên và khoa sang các module khác
                m_id = row["id"]
                for mod_list in [
                    st.session_state.m2_assignments,
                    st.session_state.m3_hsba,
                    st.session_state.m4_rx,
                    st.session_state.m5_consult,
                    st.session_state.m6_dose,
                    st.session_state.m7_counsel,
                ]:
                    for item in mod_list:
                        if item["member_id"] == m_id:
                            item["member_name"] = row["name"]
                            item["department"] = row["department"]
            st.success("Đã lưu cấu hình Khoa lâm sàng, Tính cách và Năng lực tại Module 1!")
            st.rerun()
    with c_sync_m1:
        if st.button(
            "⚡ Lưu & Tự động Phân công lại Chỉ tiêu Tuần (Chuyển sang Module 2)",
            use_container_width=True,
        ):
            for idx, row in edited_m1.iterrows():
                for col in m1_cols:
                    st.session_state.members[idx][col] = row[col]
            m2, m3, m4, m5, m6, m7 = generate_all_modules_from_auto_assignment(
                st.session_state.members, workload_scale=1.0
            )
            st.session_state.m2_assignments = m2
            st.session_state.m3_hsba = m3
            st.session_state.m4_rx = m4
            st.session_state.m5_consult = m5
            st.session_state.m6_dose = m6
            st.session_state.m7_counsel = m7
            st.success("Đã tự động phân công lại công việc & mục tiêu tuần cho toàn bộ 20 thành viên!")
            st.rerun()

# ------------------------------------------------------------------------------
# MODULE 2: TỰ ĐỘNG PHÂN CÔNG CÔNG VIỆC HÀNG TUẦN THEO KHOA, TÍNH CÁCH & NĂNG LỰC
# ------------------------------------------------------------------------------
with tab_m2:
    st.subheader("🤖 Module 2: Tự động Phân công Công việc & Định mức Mục tiêu Hàng tuần")
    st.markdown(
        """
**Cơ chế tự động phân công 3 tầng của Module 2:**
1. **Theo Khoa Lâm sàng phụ trách:** Tự động áp định mức cơ sở theo đặc thù từng khoa (VD: *Khoa ICU* ưu tiên Hội chẩn & Can thiệp chỉnh liều TDM/CRRT; *Khoa Khám bệnh Ngoại trú* ưu tiên Duyệt đơn ngoại trú & Tư vấn người bệnh; *Khoa Truyền nhiễm* ưu tiên Quản lý kháng sinh ASP & Kiểm tra HSBA).
2. **Theo Tính cách cá nhân:** Điều chỉnh trọng tâm nhiệm vụ (VD: tính cách *Chính xác số liệu* được tăng hệ số ca Chỉnh liều `+25%`; tính cách *Thấu cảm - Giao tiếp* được tăng mục tiêu Tư vấn đơn thuốc `+8%`; tính cách *Nguyên tắc - Pháp lý* được tăng định mức rà soát HSBA `+15%`).
3. **Theo Điểm Năng lực (`skill_score`):** Tự động nhân hệ số năng lực cá nhân (`skill_score / 90`) để phân bổ khối lượng công việc tuần từ Thứ 2 đến Thứ 6 vừa sức và công bằng.
"""
    )

    col_scale, col_btn_auto = st.columns([1, 2])
    with col_scale:
        workload_scale = st.slider(
            "Hệ số tải công việc toàn viện tuần này:",
            min_value=0.7,
            max_value=1.5,
            value=1.0,
            step=0.05,
            help="1.0 = Bình thường; >1.0 = Cao điểm dịch bệnh/tăng bệnh nhân nội ngoại trú",
        )
    with col_btn_auto:
        st.write("")
        if st.button(
            "🤖 Chạy Thuật toán Tự động Phân công Công việc & Đồng bộ xuống Module 3–7",
            type="primary",
            use_container_width=True,
        ):
            m2, m3, m4, m5, m6, m7 = generate_all_modules_from_auto_assignment(
                st.session_state.members, workload_scale=workload_scale
            )
            st.session_state.m2_assignments = m2
            st.session_state.m3_hsba = m3
            st.session_state.m4_rx = m4
            st.session_state.m5_consult = m5
            st.session_state.m6_dose = m6
            st.session_state.m7_counsel = m7
            st.success(
                f"Đã tự động phân công công việc tuần (Hệ số tải: {workload_scale}x) và cập nhật mục tiêu cho các Module 3, 4, 5, 6, 7!"
            )
            st.rerun()

    df_m2_view = pd.DataFrame(st.session_state.m2_assignments)
    df_m2_view = df_m2_view[df_m2_view["member_id"].isin(filtered_ids)].copy()

    edited_m2 = st.data_editor(
        df_m2_view,
        column_config={
            "member_id": st.column_config.TextColumn("Mã TV", disabled=True, width="small"),
            "member_name": st.column_config.TextColumn("Họ và tên", disabled=True, width="medium"),
            "department": st.column_config.TextColumn("Khoa Lâm sàng", disabled=True, width="medium"),
            "personality_tag": st.column_config.TextColumn("Nhóm Tính cách", disabled=True, width="medium"),
            "skill_score": st.column_config.NumberColumn("Năng lực", disabled=True, width="small"),
            "assigned_task": st.column_config.TextColumn(
                "Nội dung Công việc Tự động Phân công trong Tuần (Thứ 2 – Thứ 6)", width="large"
            ),
            "hsba_target_week": st.column_config.NumberColumn("Chỉ tiêu HSBA/Tuần", width="small"),
            "rx_out_target_week": st.column_config.NumberColumn("Chỉ tiêu Đơn Ngoại/Tuần", width="small"),
            "rx_in_target_week": st.column_config.NumberColumn("Chỉ tiêu Đơn Nội/Tuần", width="small"),
            "consult_target_week": st.column_config.NumberColumn("Chỉ tiêu Hội chẩn/Tuần", width="small"),
            "dose_target_week": st.column_config.NumberColumn("Chỉ tiêu Chỉnh liều/Tuần", width="small"),
            "rx_total_week_est": None,
            "counsel_target_pct": st.column_config.NumberColumn(
                "Mục tiêu Tư vấn (%)", format="%.1f%%", width="small"
            ),
            "assignment_completion_pct": st.column_config.ProgressColumn(
                "Tiến độ Nhiệm vụ Tuần (%)", min_value=0, max_value=100, format="%.1f%%", width="small"
            ),
        },
        use_container_width=True,
        hide_index=True,
        key="editor_module_2",
    )

    if st.button("💾 Lưu Bảng Phân công & Áp dụng Chỉ tiêu sang Module 3–7", type="primary"):
        map_m2 = {r["member_id"]: r for _, r in edited_m2.iterrows()}
        for i, item in enumerate(st.session_state.m2_assignments):
            mid = item["member_id"]
            if mid in map_m2:
                row = map_m2[mid]
                st.session_state.m2_assignments[i]["assigned_task"] = str(row["assigned_task"])
                st.session_state.m2_assignments[i]["hsba_target_week"] = int(row["hsba_target_week"])
                st.session_state.m2_assignments[i]["rx_out_target_week"] = int(row["rx_out_target_week"])
                st.session_state.m2_assignments[i]["rx_in_target_week"] = int(row["rx_in_target_week"])
                st.session_state.m2_assignments[i]["consult_target_week"] = int(row["consult_target_week"])
                st.session_state.m2_assignments[i]["dose_target_week"] = int(row["dose_target_week"])
                st.session_state.m2_assignments[i]["counsel_target_pct"] = float(row["counsel_target_pct"])
                st.session_state.m2_assignments[i]["assignment_completion_pct"] = float(
                    row["assignment_completion_pct"]
                )

        # Đồng bộ chỉ tiêu xuống Module 3, 4, 5, 6, 7
        for item in st.session_state.m3_hsba:
            if item["member_id"] in map_m2:
                item["target_week"] = int(map_m2[item["member_id"]]["hsba_target_week"])
        for item in st.session_state.m4_rx:
            if item["member_id"] in map_m2:
                item["target_out_week"] = int(map_m2[item["member_id"]]["rx_out_target_week"])
                item["target_in_week"] = int(map_m2[item["member_id"]]["rx_in_target_week"])
        for item in st.session_state.m5_consult:
            if item["member_id"] in map_m2:
                item["target_consult_week"] = int(map_m2[item["member_id"]]["consult_target_week"])
        for item in st.session_state.m6_dose:
            if item["member_id"] in map_m2:
                item["target_dose_week"] = int(map_m2[item["member_id"]]["dose_target_week"])
        for item in st.session_state.m7_counsel:
            if item["member_id"] in map_m2:
                item["target_counsel_pct"] = float(map_m2[item["member_id"]]["counsel_target_pct"])

        st.success("Đã lưu bảng phân công công việc và đồng bộ mục tiêu tuần sang toàn bộ các Module!")
        st.rerun()

# ------------------------------------------------------------------------------
# MODULE 3: TIÊU CHÍ 1 — KIỂM TRA HỒ SƠ BỆNH ÁN (THỨ 2 ĐẾN THỨ 6 & CUỐI TUẦN)
# ------------------------------------------------------------------------------
with tab_m3:
    st.subheader("📁 Module 3 (Tiêu chí 1): Kiểm tra Hồ sơ Bệnh án từ Thứ 2 đến Thứ 6 & Tổng kết Cuối tuần")
    st.caption(
        "Công thức chấm điểm độc lập Module 3: **Điểm Tiêu chí 1 = (Tổng số HSBA kiểm tra từ Thứ 2 đến Thứ 6 / Mục tiêu HSBA Tuần) × 100** (tối đa 100 điểm)."
    )

    df_m3_view = df_m3_scored[df_m3_scored["member_id"].isin(filtered_ids)].copy()
    edited_m3 = st.data_editor(
        df_m3_view,
        column_config={
            "member_id": st.column_config.TextColumn("Mã TV", disabled=True, width="small"),
            "member_name": st.column_config.TextColumn("Họ và tên Dược sĩ", disabled=True, width="medium"),
            "department": st.column_config.TextColumn("Khoa Lâm sàng", disabled=True, width="medium"),
            "target_week": st.column_config.NumberColumn(
                "Mục tiêu HSBA Tuần", min_value=1, max_value=500, step=5, width="small"
            ),
            "Thứ 2": st.column_config.NumberColumn("Thứ 2", min_value=0, max_value=200, step=1, width="small"),
            "Thứ 3": st.column_config.NumberColumn("Thứ 3", min_value=0, max_value=200, step=1, width="small"),
            "Thứ 4": st.column_config.NumberColumn("Thứ 4", min_value=0, max_value=200, step=1, width="small"),
            "Thứ 5": st.column_config.NumberColumn("Thứ 5", min_value=0, max_value=200, step=1, width="small"),
            "Thứ 6": st.column_config.NumberColumn("Thứ 6", min_value=0, max_value=200, step=1, width="small"),
            "done_week": st.column_config.NumberColumn("Tổng HSBA Cuối tuần", disabled=True, width="small"),
            "diff_week": st.column_config.NumberColumn("Chênh lệch (+/-)", disabled=True, width="small"),
            "completion_pct": st.column_config.NumberColumn("Đạt Mục tiêu (%)", disabled=True, format="%.1f%%"),
            "score_m3": st.column_config.ProgressColumn(
                "Điểm Module 3 (0-100)", min_value=0, max_value=100, format="%.1f đ", width="small"
            ),
        },
        use_container_width=True,
        hide_index=True,
        key="editor_module_3",
    )

    if st.button("💾 Lưu & Chấm điểm Module 3 (Hồ sơ Bệnh án)", type="primary"):
        map_m3 = {r["member_id"]: r for _, r in edited_m3.iterrows()}
        for i, item in enumerate(st.session_state.m3_hsba):
            mid = item["member_id"]
            if mid in map_m3:
                row = map_m3[mid]
                st.session_state.m3_hsba[i]["target_week"] = int(row["target_week"])
                for d in WEEKDAYS:
                    st.session_state.m3_hsba[i][d] = int(row[d])
        st.success("Đã cập nhật kết quả kiểm tra Hồ sơ bệnh án (Thứ 2 – Thứ 6) và tính lại Điểm Module 3!")
        st.rerun()

# ------------------------------------------------------------------------------
# MODULE 4: TIÊU CHÍ 2 — DUYỆT ĐƠN THUỐC NGOẠI TRÚ & NỘI TRÚ HÀNG NGÀY
# ------------------------------------------------------------------------------
with tab_m4:
    st.subheader("💊 Module 4 (Tiêu chí 2): Duyệt Đơn thuốc Ngoại trú & Nội trú Hàng ngày (Thứ 2 – Thứ 6)")
    st.caption(
        "Công thức chấm điểm độc lập Module 4: Kết hợp **50% Tỷ lệ hoàn thành tổng đơn duyệt trong tuần** + **25% Tỷ lệ đạt mục tiêu Đơn Ngoại trú** + **25% Tỷ lệ đạt mục tiêu Đơn Nội trú** (tối đa 100 điểm)."
    )

    df_m4_view = df_m4_scored[df_m4_scored["member_id"].isin(filtered_ids)].copy()
    edited_m4 = st.data_editor(
        df_m4_view[
            [
                "member_id",
                "member_name",
                "department",
                "target_out_week",
                "out_t2",
                "out_t3",
                "out_t4",
                "out_t5",
                "out_t6",
                "done_out_week",
                "target_in_week",
                "in_t2",
                "in_t3",
                "in_t4",
                "in_t5",
                "in_t6",
                "done_in_week",
                "score_m4",
            ]
        ],
        column_config={
            "member_id": st.column_config.TextColumn("Mã TV", disabled=True, width="small"),
            "member_name": st.column_config.TextColumn("Họ và tên", disabled=True, width="medium"),
            "department": st.column_config.TextColumn("Khoa Lâm sàng", disabled=True, width="medium"),
            "target_out_week": st.column_config.NumberColumn("Mục tiêu Ngoại/Tuần", min_value=1, max_value=2000),
            "out_t2": st.column_config.NumberColumn("Ngoại T2", min_value=0, max_value=500),
            "out_t3": st.column_config.NumberColumn("Ngoại T3", min_value=0, max_value=500),
            "out_t4": st.column_config.NumberColumn("Ngoại T4", min_value=0, max_value=500),
            "out_t5": st.column_config.NumberColumn("Ngoại T5", min_value=0, max_value=500),
            "out_t6": st.column_config.NumberColumn("Ngoại T6", min_value=0, max_value=500),
            "done_out_week": st.column_config.NumberColumn("Tổng Ngoại", disabled=True),
            "target_in_week": st.column_config.NumberColumn("Mục tiêu Nội/Tuần", min_value=1, max_value=2000),
            "in_t2": st.column_config.NumberColumn("Nội T2", min_value=0, max_value=500),
            "in_t3": st.column_config.NumberColumn("Nội T3", min_value=0, max_value=500),
            "in_t4": st.column_config.NumberColumn("Nội T4", min_value=0, max_value=500),
            "in_t5": st.column_config.NumberColumn("Nội T5", min_value=0, max_value=500),
            "in_t6": st.column_config.NumberColumn("Nội T6", min_value=0, max_value=500),
            "done_in_week": st.column_config.NumberColumn("Tổng Nội", disabled=True),
            "score_m4": st.column_config.ProgressColumn(
                "Điểm Module 4 (0-100)", min_value=0, max_value=100, format="%.1f đ"
            ),
        },
        use_container_width=True,
        hide_index=True,
        key="editor_module_4",
    )

    if st.button("💾 Lưu & Chấm điểm Module 4 (Duyệt Đơn Ngoại trú & Nội trú)", type="primary"):
        map_m4 = {r["member_id"]: r for _, r in edited_m4.iterrows()}
        for i, item in enumerate(st.session_state.m4_rx):
            mid = item["member_id"]
            if mid in map_m4:
                row = map_m4[mid]
                st.session_state.m4_rx[i]["target_out_week"] = int(row["target_out_week"])
                st.session_state.m4_rx[i]["target_in_week"] = int(row["target_in_week"])
                for c in ["out_t2", "out_t3", "out_t4", "out_t5", "out_t6", "in_t2", "in_t3", "in_t4", "in_t5", "in_t6"]:
                    st.session_state.m4_rx[i][c] = int(row[c])
        st.success("Đã cập nhật số lượng duyệt đơn Ngoại trú & Nội trú hàng ngày và tính lại Điểm Module 4!")
        st.rerun()

# ------------------------------------------------------------------------------
# MODULE 5: TIÊU CHÍ 3 — HỘI CHẨN LÂM SÀNG HÀNG NGÀY
# ------------------------------------------------------------------------------
with tab_m5:
    st.subheader("🩺 Module 5 (Tiêu chí 3): Hội chẩn Lâm sàng Hàng ngày (Thứ 2 – Thứ 6)")
    st.caption(
        "Công thức chấm điểm độc lập Module 5: **Điểm Tiêu chí 3 = 65% × (Tổng ca Hội chẩn tuần / Mục tiêu Hội chẩn tuần) + 35% × Tỷ lệ Bác sĩ đồng thuận tại buổi hội chẩn**."
    )

    df_m5_view = df_m5_scored[df_m5_scored["member_id"].isin(filtered_ids)].copy()
    edited_m5 = st.data_editor(
        df_m5_view,
        column_config={
            "member_id": st.column_config.TextColumn("Mã TV", disabled=True, width="small"),
            "member_name": st.column_config.TextColumn("Họ và tên Dược sĩ", disabled=True, width="medium"),
            "department": st.column_config.TextColumn("Khoa Lâm sàng", disabled=True, width="medium"),
            "target_consult_week": st.column_config.NumberColumn(
                "Mục tiêu Ca Hội chẩn/Tuần", min_value=1, max_value=200, step=1
            ),
            "Thứ 2": st.column_config.NumberColumn("HC Thứ 2", min_value=0, max_value=50),
            "Thứ 3": st.column_config.NumberColumn("HC Thứ 3", min_value=0, max_value=50),
            "Thứ 4": st.column_config.NumberColumn("HC Thứ 4", min_value=0, max_value=50),
            "Thứ 5": st.column_config.NumberColumn("HC Thứ 5", min_value=0, max_value=50),
            "Thứ 6": st.column_config.NumberColumn("HC Thứ 6", min_value=0, max_value=50),
            "done_consult_week": st.column_config.NumberColumn("Tổng Ca Hội chẩn", disabled=True),
            "consult_qty_pct": st.column_config.NumberColumn("Đạt Số lượng (%)", disabled=True, format="%.1f%%"),
            "doctor_consensus_pct": st.column_config.NumberColumn(
                "BS Đồng thuận Hội chẩn (%)", min_value=0.0, max_value=100.0, step=0.5, format="%.1f%%"
            ),
            "score_m5": st.column_config.ProgressColumn(
                "Điểm Module 5 (0-100)", min_value=0, max_value=100, format="%.1f đ"
            ),
        },
        use_container_width=True,
        hide_index=True,
        key="editor_module_5",
    )

    if st.button("💾 Lưu & Chấm điểm Module 5 (Hội chẩn Lâm sàng)", type="primary"):
        map_m5 = {r["member_id"]: r for _, r in edited_m5.iterrows()}
        for i, item in enumerate(st.session_state.m5_consult):
            mid = item["member_id"]
            if mid in map_m5:
                row = map_m5[mid]
                st.session_state.m5_consult[i]["target_consult_week"] = int(row["target_consult_week"])
                st.session_state.m5_consult[i]["doctor_consensus_pct"] = float(row["doctor_consensus_pct"])
                for d in WEEKDAYS:
                    st.session_state.m5_consult[i][d] = int(row[d])
        st.success("Đã cập nhật số ca hội chẩn hàng ngày và tính lại Điểm Module 5!")
        st.rerun()

# ------------------------------------------------------------------------------
# MODULE 6: TIÊU CHÍ 4 — CAN THIỆP CHỈNH LIỀU TRÊN LÂM SÀNG HÀNG NGÀY
# ------------------------------------------------------------------------------
with tab_m6:
    st.subheader("⚖️ Module 6 (Tiêu chí 4): Can thiệp Chỉnh liều trên Lâm sàng Hàng ngày (Thứ 2 – Thứ 6)")
    st.caption(
        "Công thức chấm điểm độc lập Module 6: **Điểm Tiêu chí 4 = 65% × (Tổng ca Can thiệp chỉnh liều / Mục tiêu Chỉnh liều tuần) + 35% × Tỷ lệ Can thiệp chỉnh liều được Bác sĩ chấp thuận**."
    )

    df_m6_view = df_m6_scored[df_m6_scored["member_id"].isin(filtered_ids)].copy()
    edited_m6 = st.data_editor(
        df_m6_view,
        column_config={
            "member_id": st.column_config.TextColumn("Mã TV", disabled=True, width="small"),
            "member_name": st.column_config.TextColumn("Họ và tên Dược sĩ", disabled=True, width="medium"),
            "department": st.column_config.TextColumn("Khoa Lâm sàng", disabled=True, width="medium"),
            "target_dose_week": st.column_config.NumberColumn(
                "Mục tiêu Ca Chỉnh liều/Tuần", min_value=1, max_value=200, step=1
            ),
            "Thứ 2": st.column_config.NumberColumn("CL Thứ 2", min_value=0, max_value=50),
            "Thứ 3": st.column_config.NumberColumn("CL Thứ 3", min_value=0, max_value=50),
            "Thứ 4": st.column_config.NumberColumn("CL Thứ 4", min_value=0, max_value=50),
            "Thứ 5": st.column_config.NumberColumn("CL Thứ 5", min_value=0, max_value=50),
            "Thứ 6": st.column_config.NumberColumn("CL Thứ 6", min_value=0, max_value=50),
            "done_dose_week": st.column_config.NumberColumn("Tổng Ca Chỉnh liều", disabled=True),
            "dose_qty_pct": st.column_config.NumberColumn("Đạt Số lượng (%)", disabled=True, format="%.1f%%"),
            "intervention_success_pct": st.column_config.NumberColumn(
                "Tỷ lệ Chỉnh liều Thành công (%)", min_value=0.0, max_value=100.0, step=0.5, format="%.1f%%"
            ),
            "score_m6": st.column_config.ProgressColumn(
                "Điểm Module 6 (0-100)", min_value=0, max_value=100, format="%.1f đ"
            ),
        },
        use_container_width=True,
        hide_index=True,
        key="editor_module_6",
    )

    if st.button("💾 Lưu & Chấm điểm Module 6 (Can thiệp Chỉnh liều)", type="primary"):
        map_m6 = {r["member_id"]: r for _, r in edited_m6.iterrows()}
        for i, item in enumerate(st.session_state.m6_dose):
            mid = item["member_id"]
            if mid in map_m6:
                row = map_m6[mid]
                st.session_state.m6_dose[i]["target_dose_week"] = int(row["target_dose_week"])
                st.session_state.m6_dose[i]["intervention_success_pct"] = float(
                    row["intervention_success_pct"]
                )
                for d in WEEKDAYS:
                    st.session_state.m6_dose[i][d] = int(row[d])
        st.success("Đã cập nhật số ca can thiệp chỉnh liều hàng ngày và tính lại Điểm Module 6!")
        st.rerun()

# ------------------------------------------------------------------------------
# MODULE 7: TIÊU CHÍ 5 — TƯ VẤN ĐƠN THUỐC TRÊN TỔNG SỐ ĐƠN TRONG NGÀY
# ------------------------------------------------------------------------------
with tab_m7:
    st.subheader("🗣️ Module 7 (Tiêu chí 5): Tư vấn Đơn thuốc trên Tổng số Đơn thuốc trong Ngày (Thứ 2 – Thứ 6)")
    st.caption(
        "Công thức chấm điểm độc lập Module 7: Tính **Tỷ lệ Tư vấn Thực tế (%) = (Tổng số đơn được tư vấn / Tổng số đơn phát sinh trong ngày) × 100%**, sau đó đối chiếu với **Mục tiêu Tỷ lệ Tư vấn (%)** để quy đổi ra **Điểm Module 7 (0–100)**."
    )

    df_m7_view = df_m7_scored[df_m7_scored["member_id"].isin(filtered_ids)].copy()
    edited_m7 = st.data_editor(
        df_m7_view[
            [
                "member_id",
                "member_name",
                "department",
                "target_counsel_pct",
                "coun_t2",
                "tot_t2",
                "coun_t3",
                "tot_t3",
                "coun_t4",
                "tot_t4",
                "coun_t5",
                "tot_t5",
                "coun_t6",
                "tot_t6",
                "counseled_week",
                "total_rx_week",
                "actual_counsel_pct",
                "score_m7",
            ]
        ],
        column_config={
            "member_id": st.column_config.TextColumn("Mã TV", disabled=True, width="small"),
            "member_name": st.column_config.TextColumn("Họ và tên", disabled=True, width="medium"),
            "department": st.column_config.TextColumn("Khoa Lâm sàng", disabled=True, width="medium"),
            "target_counsel_pct": st.column_config.NumberColumn(
                "Mục tiêu Tỷ lệ Tư vấn (%)", min_value=10.0, max_value=100.0, step=1.0, format="%.1f%%"
            ),
            "coun_t2": st.column_config.NumberColumn("Tư vấn T2", min_value=0, max_value=1000),
            "tot_t2": st.column_config.NumberColumn("Tổng đơn T2", min_value=1, max_value=1000),
            "coun_t3": st.column_config.NumberColumn("Tư vấn T3", min_value=0, max_value=1000),
            "tot_t3": st.column_config.NumberColumn("Tổng đơn T3", min_value=1, max_value=1000),
            "coun_t4": st.column_config.NumberColumn("Tư vấn T4", min_value=0, max_value=1000),
            "tot_t4": st.column_config.NumberColumn("Tổng đơn T4", min_value=1, max_value=1000),
            "coun_t5": st.column_config.NumberColumn("Tư vấn T5", min_value=0, max_value=1000),
            "tot_t5": st.column_config.NumberColumn("Tổng đơn T5", min_value=1, max_value=1000),
            "coun_t6": st.column_config.NumberColumn("Tư vấn T6", min_value=0, max_value=1000),
            "tot_t6": st.column_config.NumberColumn("Tổng đơn T6", min_value=1, max_value=1000),
            "counseled_week": st.column_config.NumberColumn("Tổng Đơn Tư vấn", disabled=True),
            "total_rx_week": st.column_config.NumberColumn("Tổng Đơn Tuần", disabled=True),
            "actual_counsel_pct": st.column_config.NumberColumn(
                "Tỷ lệ Thực tế (%)", disabled=True, format="%.1f%%"
            ),
            "score_m7": st.column_config.ProgressColumn(
                "Điểm Module 7 (0-100)", min_value=0, max_value=100, format="%.1f đ"
            ),
        },
        use_container_width=True,
        hide_index=True,
        key="editor_module_7",
    )

    if st.button("💾 Lưu & Chấm điểm Module 7 (Tư vấn Đơn thuốc / Tổng đơn)", type="primary"):
        map_m7 = {r["member_id"]: r for _, r in edited_m7.iterrows()}
        for i, item in enumerate(st.session_state.m7_counsel):
            mid = item["member_id"]
            if mid in map_m7:
                row = map_m7[mid]
                st.session_state.m7_counsel[i]["target_counsel_pct"] = float(row["target_counsel_pct"])
                for d_num in ["2", "3", "4", "5", "6"]:
                    c_val = int(row[f"coun_t{d_num}"])
                    t_val = max(int(row[f"tot_t{d_num}"]), c_val, 1)
                    st.session_state.m7_counsel[i][f"coun_t{d_num}"] = c_val
                    st.session_state.m7_counsel[i][f"tot_t{d_num}"] = t_val
        st.success("Đã cập nhật số đơn tư vấn trên tổng số đơn hàng ngày và tính lại Điểm Module 7!")
        st.rerun()

# ------------------------------------------------------------------------------
# MODULE 8: TỔNG HỢP & TÍNH KPI TOÀN DIỆN TỪ TẤT CẢ CÁC MODULE
# ------------------------------------------------------------------------------
with tab_m8:
    st.subheader("🏆 Module 8: Bảng Tổng hợp Điểm Tất cả Tiêu chí & Đánh giá KPI Cuối tuần")
    st.markdown(
        f"""
**Công thức Tổng hợp KPI tại Module 8 (Tự động kết nối các Module độc lập):**
- **Module 3 (Kiểm tra HSBA Tuần):** Trọng số `{w_m3_hsba}%`
- **Module 4 (Duyệt Đơn Ngoại trú & Nội trú):** Trọng số `{w_m4_rx}%`
- **Module 5 (Hội chẩn Lâm sàng):** Trọng số `{w_m5_consult}%`
- **Module 6 (Can thiệp Chỉnh liều):** Trọng số `{w_m6_dose}%`
- **Module 7 (Tư vấn Đơn thuốc / Tổng đơn):** Trọng số `{w_m7_counsel}%`
- **Module 2 (Hoàn thành Công việc Phân công Tuần):** Trọng số `{w_m2_task}%`
"""
    )

    df_kpi_sorted = df_master_filtered.sort_values(by="kpi_total", ascending=False).copy()

    st.dataframe(
        df_kpi_sorted[
            [
                "id",
                "name",
                "department",
                "personality_tag",
                "score_m3",
                "score_m4",
                "score_m5",
                "score_m6",
                "score_m7",
                "assignment_completion_pct",
                "kpi_total",
                "kpi_rank",
            ]
        ],
        column_config={
            "id": "Mã TV",
            "name": "Họ và tên Dược sĩ",
            "department": "Khoa Lâm sàng",
            "personality_tag": "Nhóm Tính cách",
            "score_m3": st.column_config.NumberColumn("Điểm M3 (HSBA)", format="%.1f"),
            "score_m4": st.column_config.NumberColumn("Điểm M4 (Duyệt đơn)", format="%.1f"),
            "score_m5": st.column_config.NumberColumn("Điểm M5 (Hội chẩn)", format="%.1f"),
            "score_m6": st.column_config.NumberColumn("Điểm M6 (Chỉnh liều)", format="%.1f"),
            "score_m7": st.column_config.NumberColumn("Điểm M7 (Tư vấn)", format="%.1f"),
            "assignment_completion_pct": st.column_config.NumberColumn("Điểm M2 (Phân công)", format="%.1f"),
            "kpi_total": st.column_config.ProgressColumn(
                "TỔNG ĐIỂM KPI (0-100)", min_value=0, max_value=100, format="%.1f đ"
            ),
            "kpi_rank": "Xếp loại KPI",
        },
        use_container_width=True,
        hide_index=True,
    )

    csv_master = df_kpi_sorted.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 Xuất Bảng Tổng hợp KPI Toàn diện (8 Module) ra Excel (CSV)",
        data=csv_master,
        file_name="bang_kpi_toan_dien_8_module_dls.csv",
        mime="text/csv",
    )

    ch1, ch2 = st.columns(2)
    with ch1:
        st.markdown("##### 📈 Biểu đồ Tổng Điểm KPI & Điểm Thành phần (Module 3 – Module 7)")
        chart_scores = df_kpi_sorted.set_index("name")[
            ["kpi_total", "score_m3", "score_m4", "score_m5", "score_m6", "score_m7"]
        ]
        chart_scores.columns = [
            "Tổng KPI",
            "M3: HSBA",
            "M4: Duyệt đơn",
            "M5: Hội chẩn",
            "M6: Chỉnh liều",
            "M7: Tư vấn",
        ]
        st.bar_chart(chart_scores, height=460)

    with ch2:
        st.markdown("##### 📊 Điểm KPI Trung bình theo Khoa Lâm sàng Phụ trách")
        dept_kpi = (
            df_kpi_sorted.groupby("department", as_index=True)
            .agg(
                Điểm_KPI_TB=("kpi_total", "mean"),
                Điểm_HSBA_M3=("score_m3", "mean"),
                Điểm_Chỉnh_Liều_M6=("score_m6", "mean"),
            )
            .round(1)
        )
        st.bar_chart(dept_kpi, height=460)