import io
import json
import os
from datetime import datetime
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Hệ thống Quản trị & Chấm điểm KPI Đa Module - Tổ Dược Lâm Sàng",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

STATE_VERSION = "v4.0_excel_live_sync"
AUTOSAVE_FILE = "kpi_dls_autosave.json"
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
# MODULE 1: DỮ LIỆU GỐC 20 THÀNH VIÊN
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
# MODULE 2: THUẬT TOÁN TÍNH CHỈ TIÊU & KHỞI TẠO DỮ LIỆU
# ==============================================================================
def auto_assign_weekly_plan_for_member(member, workload_scale=1.0):
    dept = member.get("department", CLINICAL_DEPARTMENTS[0])
    p_tag = member.get("personality_tag", PERSONALITY_TAGS[0])
    skill = float(member.get("skill_score", 90))

    base_prof = DEPARTMENT_WORKLOAD_PROFILE.get(
        dept, DEPARTMENT_WORKLOAD_PROFILE[CLINICAL_DEPARTMENTS[0]]
    )
    p_mod = PERSONALITY_MODIFIERS.get(p_tag, PERSONALITY_MODIFIERS[PERSONALITY_TAGS[0]])

    skill_factor = max(0.75, min(1.25, skill / 90.0)) * float(workload_scale)

    hsba_target_week = max(0, int(round(base_prof["hsba_week"] * p_mod["hsba"] * skill_factor / 5.0) * 5))
    rx_out_target_week = max(0, int(round(base_prof["rx_out_day"] * 5 * p_mod["rx"] * skill_factor / 5.0) * 5))
    rx_in_target_week = max(0, int(round(base_prof["rx_in_day"] * 5 * p_mod["rx"] * skill_factor / 5.0) * 5))
    consult_target_week = max(0, int(round(base_prof["consult_week"] * p_mod["consult"] * skill_factor)))
    dose_target_week = max(0, int(round(base_prof["dose_week"] * p_mod["dose"] * skill_factor)))
    rx_total_week_est = max(
        rx_out_target_week + rx_in_target_week,
        int(round(base_prof["rx_total_day"] * 5 * skill_factor)),
    )
    counsel_target_pct = round(min(100.0, max(50.0, base_prof["counsel_target_pct"] * p_mod["counsel"])), 1)

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


def generate_all_modules_from_auto_assignment(members_list, workload_scale=1.0, zero_actuals=False):
    m2_assignments, m3_hsba, m4_rx, m5_consult, m6_dose, m7_counsel = [], [], [], [], [], []

    for idx, m in enumerate(members_list):
        plan = auto_assign_weekly_plan_for_member(m, workload_scale=workload_scale)
        m2_assignments.append(plan)

        base_hsba_d = 0 if zero_actuals else (plan["hsba_target_week"] // 5)
        m3_hsba.append(
            {
                "member_id": m["id"],
                "member_name": m["name"],
                "department": m["department"],
                "target_week": plan["hsba_target_week"],
                "Thứ 2": 0 if zero_actuals else base_hsba_d + (1 if idx % 3 == 0 else 0),
                "Thứ 3": 0 if zero_actuals else base_hsba_d,
                "Thứ 4": 0 if zero_actuals else max(0, base_hsba_d + (1 if idx % 2 == 0 else -1)),
                "Thứ 5": 0 if zero_actuals else base_hsba_d,
                "Thứ 6": 0 if zero_actuals else base_hsba_d + (1 if idx % 4 == 0 else 0),
            }
        )

        out_d = 0 if zero_actuals else (plan["rx_out_target_week"] // 5)
        in_d = 0 if zero_actuals else (plan["rx_in_target_week"] // 5)
        m4_rx.append(
            {
                "member_id": m["id"],
                "member_name": m["name"],
                "department": m["department"],
                "target_out_week": plan["rx_out_target_week"],
                "target_in_week": plan["rx_in_target_week"],
                "out_t2": 0 if zero_actuals else out_d,
                "out_t3": 0 if zero_actuals else out_d + 2,
                "out_t4": 0 if zero_actuals else max(0, out_d - 1),
                "out_t5": 0 if zero_actuals else out_d + 1,
                "out_t6": 0 if zero_actuals else out_d,
                "in_t2": 0 if zero_actuals else in_d,
                "in_t3": 0 if zero_actuals else in_d + 1,
                "in_t4": 0 if zero_actuals else in_d,
                "in_t5": 0 if zero_actuals else in_d + 1,
                "in_t6": 0 if zero_actuals else max(0, in_d - 1),
            }
        )

        con_d = 0 if zero_actuals else max(1, plan["consult_target_week"] // 5)
        m5_consult.append(
            {
                "member_id": m["id"],
                "member_name": m["name"],
                "department": m["department"],
                "target_consult_week": plan["consult_target_week"],
                "Thứ 2": 0 if zero_actuals else con_d,
                "Thứ 3": 0 if zero_actuals else con_d + (1 if idx % 2 == 0 else 0),
                "Thứ 4": 0 if zero_actuals else con_d,
                "Thứ 5": 0 if zero_actuals else con_d + (1 if idx % 3 == 0 else 0),
                "Thứ 6": 0 if zero_actuals else con_d,
                "doctor_consensus_pct": round(93.0 + (idx % 6) * 1.0, 1),
            }
        )

        dose_d = 0 if zero_actuals else max(1, plan["dose_target_week"] // 5)
        m6_dose.append(
            {
                "member_id": m["id"],
                "member_name": m["name"],
                "department": m["department"],
                "target_dose_week": plan["dose_target_week"],
                "Thứ 2": 0 if zero_actuals else dose_d,
                "Thứ 3": 0 if zero_actuals else dose_d + 1,
                "Thứ 4": 0 if zero_actuals else dose_d,
                "Thứ 5": 0 if zero_actuals else dose_d + (1 if idx % 2 == 1 else 0),
                "Thứ 6": 0 if zero_actuals else dose_d,
                "intervention_success_pct": round(94.0 + (idx % 5) * 1.0, 1),
            }
        )

        tot_d = 0 if zero_actuals else max(10, plan["rx_total_week_est"] // 5)
        coun_d = 0 if zero_actuals else min(tot_d, int(round(tot_d * (plan["counsel_target_pct"] / 100.0))))
        m7_counsel.append(
            {
                "member_id": m["id"],
                "member_name": m["name"],
                "department": m["department"],
                "target_counsel_pct": plan["counsel_target_pct"],
                "coun_t2": coun_d,
                "tot_t2": tot_d,
                "coun_t3": 0 if zero_actuals else min(tot_d + 2, coun_d + 2),
                "tot_t3": 0 if zero_actuals else tot_d + 2,
                "coun_t4": coun_d,
                "tot_t4": tot_d,
                "coun_t5": 0 if zero_actuals else min(tot_d + 1, coun_d + 1),
                "tot_t5": 0 if zero_actuals else tot_d + 1,
                "coun_t6": coun_d,
                "tot_t6": tot_d,
            }
        )

    return m2_assignments, m3_hsba, m4_rx, m5_consult, m6_dose, m7_counsel


def recalculate_targets_keep_actuals(workload_scale=1.0):
    """Chỉ tính toán lại Định mức Mục tiêu theo Khoa/Tính cách/Năng lực, GIỮ NGUYÊN số thực tế Thứ 2 - Thứ 6."""
    old_m2_map = {item["member_id"]: item for item in st.session_state.m2_assignments}
    new_m2 = []
    plan_map = {}

    for m in st.session_state.members:
        plan = auto_assign_weekly_plan_for_member(m, workload_scale=workload_scale)
        if m["id"] in old_m2_map:
            plan["assignment_completion_pct"] = float(
                old_m2_map[m["id"]].get("assignment_completion_pct", plan["assignment_completion_pct"])
            )
        new_m2.append(plan)
        plan_map[m["id"]] = plan

    st.session_state.m2_assignments = new_m2

    for item in st.session_state.m3_hsba:
        mid = item["member_id"]
        if mid in plan_map:
            item["member_name"] = plan_map[mid]["member_name"]
            item["department"] = plan_map[mid]["department"]
            item["target_week"] = plan_map[mid]["hsba_target_week"]

    for item in st.session_state.m4_rx:
        mid = item["member_id"]
        if mid in plan_map:
            item["member_name"] = plan_map[mid]["member_name"]
            item["department"] = plan_map[mid]["department"]
            item["target_out_week"] = plan_map[mid]["rx_out_target_week"]
            item["target_in_week"] = plan_map[mid]["rx_in_target_week"]

    for item in st.session_state.m5_consult:
        mid = item["member_id"]
        if mid in plan_map:
            item["member_name"] = plan_map[mid]["member_name"]
            item["department"] = plan_map[mid]["department"]
            item["target_consult_week"] = plan_map[mid]["consult_target_week"]

    for item in st.session_state.m6_dose:
        mid = item["member_id"]
        if mid in plan_map:
            item["member_name"] = plan_map[mid]["member_name"]
            item["department"] = plan_map[mid]["department"]
            item["target_dose_week"] = plan_map[mid]["dose_target_week"]

    for item in st.session_state.m7_counsel:
        mid = item["member_id"]
        if mid in plan_map:
            item["member_name"] = plan_map[mid]["member_name"]
            item["department"] = plan_map[mid]["department"]
            item["target_counsel_pct"] = plan_map[mid]["counsel_target_pct"]


# ==============================================================================
# CÁC HÀM CHẤM ĐIỂM CHUẨN EXCEL THỰC TẾ (XỬ LÝ ĐÚNG TRƯỜNG HỢP MỤC TIÊU = 0)
# ==============================================================================
def score_module_3_hsba(m3_list, max_cap=100.0):
    df = pd.DataFrame(m3_list).copy()
    for d in WEEKDAYS:
        df[d] = pd.to_numeric(df[d], errors="coerce").fillna(0).clip(lower=0).astype(int)
    df["target_week"] = pd.to_numeric(df["target_week"], errors="coerce").fillna(0).clip(lower=0).astype(int)
    df["done_week"] = df[WEEKDAYS].sum(axis=1)
    df["diff_week"] = df["done_week"] - df["target_week"]

    def calc_pct(row):
        t = row["target_week"]
        d = row["done_week"]
        if t <= 0:
            return 100.0
        return round((d / t) * 100.0, 1)

    df["completion_pct"] = df.apply(calc_pct, axis=1)
    df["score_m3"] = df["completion_pct"].clip(0.0, float(max_cap)).round(1)
    return df


def score_module_4_prescription(m4_list, max_cap=100.0):
    df = pd.DataFrame(m4_list).copy()
    out_cols = ["out_t2", "out_t3", "out_t4", "out_t5", "out_t6"]
    in_cols = ["in_t2", "in_t3", "in_t4", "in_t5", "in_t6"]
    for c in out_cols + in_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).clip(lower=0).astype(int)
    df["target_out_week"] = pd.to_numeric(df["target_out_week"], errors="coerce").fillna(0).clip(lower=0).astype(int)
    df["target_in_week"] = pd.to_numeric(df["target_in_week"], errors="coerce").fillna(0).clip(lower=0).astype(int)

    df["done_out_week"] = df[out_cols].sum(axis=1)
    df["done_in_week"] = df[in_cols].sum(axis=1)
    df["done_total_rx"] = df["done_out_week"] + df["done_in_week"]
    df["target_total_rx"] = df["target_out_week"] + df["target_in_week"]

    def calc_row_m4(row):
        t_out, d_out = row["target_out_week"], row["done_out_week"]
        t_in, d_in = row["target_in_week"], row["done_in_week"]
        t_tot, d_tot = row["target_total_rx"], row["done_total_rx"]

        out_pct = (d_out / t_out * 100.0) if t_out > 0 else 100.0
        in_pct = (d_in / t_in * 100.0) if t_in > 0 else 100.0
        tot_pct = (d_tot / t_tot * 100.0) if t_tot > 0 else 100.0

        c_out = min(float(max_cap), max(0.0, out_pct))
        c_in = min(float(max_cap), max(0.0, in_pct))
        c_tot = min(float(max_cap), max(0.0, tot_pct))

        # Chuẩn thực tế Excel: Không phạt Dược sĩ Nội trú có mục tiêu Ngoại trú = 0 (và ngược lại)
        if t_out > 0 and t_in > 0:
            score = 0.5 * c_tot + 0.25 * c_out + 0.25 * c_in
        elif t_out > 0 and t_in == 0:
            score = c_out
        elif t_in > 0 and t_out == 0:
            score = c_in
        else:
            score = 100.0
        return pd.Series([round(out_pct, 1), round(in_pct, 1), round(score, 1)])

    df[["out_pct", "in_pct", "score_m4"]] = df.apply(calc_row_m4, axis=1)
    return df


def score_module_5_consultation(m5_list, max_cap=100.0):
    df = pd.DataFrame(m5_list).copy()
    for d in WEEKDAYS:
        df[d] = pd.to_numeric(df[d], errors="coerce").fillna(0).clip(lower=0).astype(int)
    df["target_consult_week"] = (
        pd.to_numeric(df["target_consult_week"], errors="coerce").fillna(0).clip(lower=0).astype(int)
    )
    df["doctor_consensus_pct"] = (
        pd.to_numeric(df["doctor_consensus_pct"], errors="coerce").fillna(90.0).clip(0.0, 100.0)
    )
    df["done_consult_week"] = df[WEEKDAYS].sum(axis=1)

    def calc_row_m5(row):
        t = row["target_consult_week"]
        d = row["done_consult_week"]
        cons = row["doctor_consensus_pct"]
        if t <= 0:
            return pd.Series([100.0, 100.0])
        if d <= 0:
            # Nếu không thực hiện ca hội chẩn nào thì điểm = 0 (không cộng điểm đồng thuận khống)
            return pd.Series([0.0, 0.0])
        qty_pct = (d / t) * 100.0
        score = 0.65 * min(float(max_cap), qty_pct) + 0.35 * cons
        return pd.Series([round(qty_pct, 1), round(min(float(max_cap), score), 1)])

    df[["consult_qty_pct", "score_m5"]] = df.apply(calc_row_m5, axis=1)
    return df


def score_module_6_dose_intervention(m6_list, max_cap=100.0):
    df = pd.DataFrame(m6_list).copy()
    for d in WEEKDAYS:
        df[d] = pd.to_numeric(df[d], errors="coerce").fillna(0).clip(lower=0).astype(int)
    df["target_dose_week"] = (
        pd.to_numeric(df["target_dose_week"], errors="coerce").fillna(0).clip(lower=0).astype(int)
    )
    df["intervention_success_pct"] = (
        pd.to_numeric(df["intervention_success_pct"], errors="coerce").fillna(92.0).clip(0.0, 100.0)
    )
    df["done_dose_week"] = df[WEEKDAYS].sum(axis=1)

    def calc_row_m6(row):
        t = row["target_dose_week"]
        d = row["done_dose_week"]
        succ = row["intervention_success_pct"]
        if t <= 0:
            return pd.Series([100.0, 100.0])
        if d <= 0:
            return pd.Series([0.0, 0.0])
        qty_pct = (d / t) * 100.0
        score = 0.65 * min(float(max_cap), qty_pct) + 0.35 * succ
        return pd.Series([round(qty_pct, 1), round(min(float(max_cap), score), 1)])

    df[["dose_qty_pct", "score_m6"]] = df.apply(calc_row_m6, axis=1)
    return df


def score_module_7_counseling(m7_list, max_cap=100.0):
    df = pd.DataFrame(m7_list).copy()
    c_cols = ["coun_t2", "coun_t3", "coun_t4", "coun_t5", "coun_t6"]
    t_cols = ["tot_t2", "tot_t3", "tot_t4", "tot_t5", "tot_t6"]
    for c in c_cols + t_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).clip(lower=0).astype(int)
    df["target_counsel_pct"] = (
        pd.to_numeric(df["target_counsel_pct"], errors="coerce").fillna(80.0).clip(0.0, 100.0)
    )

    df["counseled_week"] = df[c_cols].sum(axis=1)
    df["total_rx_week"] = df[t_cols].sum(axis=1)

    def calc_row_m7(row):
        c_w = row["counseled_week"]
        t_w = row["total_rx_week"]
        target_pct = row["target_counsel_pct"]
        if target_pct <= 0:
            return pd.Series([100.0, 100.0])
        if t_w <= 0:
            return pd.Series([0.0, 0.0])
        actual_pct = min(100.0, (c_w / t_w) * 100.0)
        score = min(float(max_cap), (actual_pct / target_pct) * 100.0)
        return pd.Series([round(actual_pct, 1), round(score, 1)])

    df[["actual_counsel_pct", "score_m7"]] = df.apply(calc_row_m7, axis=1)
    return df


def compute_master_kpi_module8(members_list, m2_list, df_m3, df_m4, df_m5, df_m6, df_m7, weights):
    df_base = pd.DataFrame(members_list)[
        ["id", "name", "code_role", "subsystem", "department", "personality_tag", "skill_score", "sla_compliance"]
    ].copy()
    df_m2 = pd.DataFrame(m2_list)[["member_id", "assigned_task", "assignment_completion_pct"]].copy()

    merged = (
        df_base.merge(df_m2, left_on="id", right_on="member_id", how="left")
        .drop(columns=["member_id"])
        .merge(df_m3[["member_id", "done_week", "target_week", "score_m3"]], left_on="id", right_on="member_id", how="left")
        .drop(columns=["member_id"])
        .merge(
            df_m4[["member_id", "done_out_week", "target_out_week", "done_in_week", "target_in_week", "done_total_rx", "target_total_rx", "score_m4"]],
            left_on="id",
            right_on="member_id",
            how="left",
        )
        .drop(columns=["member_id"])
        .merge(df_m5[["member_id", "done_consult_week", "target_consult_week", "score_m5"]], left_on="id", right_on="member_id", how="left")
        .drop(columns=["member_id"])
        .merge(df_m6[["member_id", "done_dose_week", "target_dose_week", "score_m6"]], left_on="id", right_on="member_id", how="left")
        .drop(columns=["member_id"])
        .merge(df_m7[["member_id", "counseled_week", "total_rx_week", "actual_counsel_pct", "target_counsel_pct", "score_m7"]], left_on="id", right_on="member_id", how="left")
        .drop(columns=["member_id"])
    )

    for s_col in ["score_m3", "score_m4", "score_m5", "score_m6", "score_m7", "assignment_completion_pct"]:
        merged[s_col] = pd.to_numeric(merged[s_col], errors="coerce").fillna(0.0)

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
# CƠ CHẾ AUTO-SAVE XUỐNG Ổ CỨNG & XUẤT/NHẬP EXCEL (.XLSX) ĐA SHEET
# ==============================================================================
def get_current_payload():
    return {
        "app_version": STATE_VERSION,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "weights": st.session_state.get(
            "weights",
            {
                "w_m3_hsba": 25,
                "w_m4_rx": 20,
                "w_m5_consult": 15,
                "w_m6_dose": 15,
                "w_m7_counsel": 15,
                "w_m2_task": 10,
            },
        ),
        "max_score_cap": st.session_state.get("max_score_cap", 100.0),
        "members": st.session_state.members,
        "m2_assignments": st.session_state.m2_assignments,
        "m3_hsba": st.session_state.m3_hsba,
        "m4_rx": st.session_state.m4_rx,
        "m5_consult": st.session_state.m5_consult,
        "m6_dose": st.session_state.m6_dose,
        "m7_counsel": st.session_state.m7_counsel,
    }


def save_state_to_disk():
    """Tự động lưu toàn bộ dữ liệu xuống file JSON cục bộ mỗi khi sửa thông số trên Web."""
    try:
        payload = get_current_payload()
        with open(AUTOSAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        st.session_state.last_saved_time = payload["updated_at"]
    except Exception:
        pass


def load_state_from_disk():
    if os.path.exists(AUTOSAVE_FILE):
        try:
            with open(AUTOSAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if "members" in data and "m3_hsba" in data:
                return data
        except Exception:
            return None
    return None


def ensure_session_state_initialized(force_reset=False):
    if "editor_ver" not in st.session_state:
        st.session_state.editor_ver = 0

    if not force_reset and st.session_state.get("app_version") == STATE_VERSION:
        return

    saved_data = None if force_reset else load_state_from_disk()
    if saved_data is not None:
        st.session_state.app_version = STATE_VERSION
        st.session_state.members = saved_data["members"]
        st.session_state.m2_assignments = saved_data["m2_assignments"]
        st.session_state.m3_hsba = saved_data["m3_hsba"]
        st.session_state.m4_rx = saved_data["m4_rx"]
        st.session_state.m5_consult = saved_data["m5_consult"]
        st.session_state.m6_dose = saved_data["m6_dose"]
        st.session_state.m7_counsel = saved_data["m7_counsel"]
        st.session_state.weights = saved_data.get(
            "weights",
            {
                "w_m3_hsba": 25,
                "w_m4_rx": 20,
                "w_m5_consult": 15,
                "w_m6_dose": 15,
                "w_m7_counsel": 15,
                "w_m2_task": 10,
            },
        )
        st.session_state.max_score_cap = float(saved_data.get("max_score_cap", 100.0))
        st.session_state.last_saved_time = saved_data.get("updated_at", "Đã khôi phục từ ổ cứng")
    else:
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
        st.session_state.weights = {
            "w_m3_hsba": 25,
            "w_m4_rx": 20,
            "w_m5_consult": 15,
            "w_m6_dose": 15,
            "w_m7_counsel": 15,
            "w_m2_task": 10,
        }
        st.session_state.max_score_cap = 100.0
        st.session_state.editor_ver += 1
        save_state_to_disk()


def export_all_to_excel_bytes(df_master, df_m3, df_m4, df_m5, df_m6, df_m7):
    """Xuất toàn bộ 8 Module & Trọng số ra 1 file Excel (.xlsx) đa Sheet chuẩn thực tế."""
    output = io.BytesIO()
    engine_used = None
    for eng in ["openpyxl", "xlsxwriter"]:
        try:
            with pd.ExcelWriter(output, engine=eng) as writer:
                df_master.to_excel(writer, sheet_name="M8_TongHop_KPI", index=False)
                pd.DataFrame(st.session_state.members).to_excel(writer, sheet_name="M1_NhanSu", index=False)
                pd.DataFrame(st.session_state.m2_assignments).to_excel(writer, sheet_name="M2_PhanCong", index=False)
                df_m3.to_excel(writer, sheet_name="M3_HSBA", index=False)
                df_m4.to_excel(writer, sheet_name="M4_DuyetDon", index=False)
                df_m5.to_excel(writer, sheet_name="M5_HoiChan", index=False)
                df_m6.to_excel(writer, sheet_name="M6_ChinhLieu", index=False)
                df_m7.to_excel(writer, sheet_name="M7_TuVan", index=False)
                pd.DataFrame([st.session_state.weights]).to_excel(writer, sheet_name="CauHinh_TrongSo", index=False)
            engine_used = eng
            break
        except ImportError:
            output = io.BytesIO()
            continue

    if engine_used is None:
        return None
    return output.getvalue()


def import_from_excel_file(uploaded_excel):
    """Đọc dữ liệu từ file Excel (.xlsx) nhiều Sheet và nạp đồng bộ vào 8 Module."""
    sheets = pd.read_excel(uploaded_excel, sheet_name=None)
    if "M1_NhanSu" in sheets:
        st.session_state.members = sheets["M1_NhanSu"].to_dict(orient="records")
    if "M2_PhanCong" in sheets:
        st.session_state.m2_assignments = sheets["M2_PhanCong"].to_dict(orient="records")
    if "M3_HSBA" in sheets:
        cols_m3 = ["member_id", "member_name", "department", "target_week"] + WEEKDAYS
        df3 = sheets["M3_HSBA"]
        avail3 = [c for c in cols_m3 if c in df3.columns]
        st.session_state.m3_hsba = df3[avail3].to_dict(orient="records")
    if "M4_DuyetDon" in sheets:
        cols_m4 = [
            "member_id", "member_name", "department", "target_out_week", "target_in_week",
            "out_t2", "out_t3", "out_t4", "out_t5", "out_t6",
            "in_t2", "in_t3", "in_t4", "in_t5", "in_t6",
        ]
        df4 = sheets["M4_DuyetDon"]
        avail4 = [c for c in cols_m4 if c in df4.columns]
        st.session_state.m4_rx = df4[avail4].to_dict(orient="records")
    if "M5_HoiChan" in sheets:
        cols_m5 = ["member_id", "member_name", "department", "target_consult_week"] + WEEKDAYS + ["doctor_consensus_pct"]
        df5 = sheets["M5_HoiChan"]
        avail5 = [c for c in cols_m5 if c in df5.columns]
        st.session_state.m5_consult = df5[avail5].to_dict(orient="records")
    if "M6_ChinhLieu" in sheets:
        cols_m6 = ["member_id", "member_name", "department", "target_dose_week"] + WEEKDAYS + ["intervention_success_pct"]
        df6 = sheets["M6_ChinhLieu"]
        avail6 = [c for c in cols_m6 if c in df6.columns]
        st.session_state.m6_dose = df6[avail6].to_dict(orient="records")
    if "M7_TuVan" in sheets:
        cols_m7 = [
            "member_id", "member_name", "department", "target_counsel_pct",
            "coun_t2", "tot_t2", "coun_t3", "tot_t3", "coun_t4", "tot_t4",
            "coun_t5", "tot_t5", "coun_t6", "tot_t6",
        ]
        df7 = sheets["M7_TuVan"]
        avail7 = [c for c in cols_m7 if c in df7.columns]
        st.session_state.m7_counsel = df7[avail7].to_dict(orient="records")
    if "CauHinh_TrongSo" in sheets and not sheets["CauHinh_TrongSo"].empty:
        w_row = sheets["CauHinh_TrongSo"].iloc[0].to_dict()
        for k in st.session_state.weights:
            if k in w_row and pd.notna(w_row[k]):
                st.session_state.weights[k] = int(w_row[k])

    st.session_state.editor_ver += 1
    save_state_to_disk()


# ==============================================================================
# CÁC HÀM CALLBACK TỰ ĐỘNG LƯU TỨC THỜI KHI SỬA BẢNG (LIVE EXCEL SYNC)
# ==============================================================================
def sync_m2_target_field(member_id, m2_field, value):
    for item in st.session_state.m2_assignments:
        if item["member_id"] == member_id:
            item[m2_field] = value
            break


def cb_sync_module_1():
    key = f"editor_module_1_{st.session_state.editor_ver}"
    changes = st.session_state.get(key, {}).get("edited_rows", {})
    view_ids = st.session_state.get("_view_ids_m1", [])
    if not changes:
        return
    for r_idx_str, cols in changes.items():
        r_idx = int(r_idx_str)
        if r_idx < len(view_ids):
            mid = view_ids[r_idx]
            for m in st.session_state.members:
                if m["id"] == mid:
                    for c, val in cols.items():
                        m[c] = val
                    # Đồng bộ tên, khoa, tính cách, năng lực sang các Module 2-7
                    for mod_list in [
                        st.session_state.m2_assignments,
                        st.session_state.m3_hsba,
                        st.session_state.m4_rx,
                        st.session_state.m5_consult,
                        st.session_state.m6_dose,
                        st.session_state.m7_counsel,
                    ]:
                        for item in mod_list:
                            if item["member_id"] == mid:
                                item["member_name"] = m["name"]
                                item["department"] = m["department"]
                                if "personality_tag" in item:
                                    item["personality_tag"] = m["personality_tag"]
                                if "skill_score" in item:
                                    item["skill_score"] = int(m["skill_score"])
                    break
    save_state_to_disk()


def cb_sync_module_2():
    key = f"editor_module_2_{st.session_state.editor_ver}"
    changes = st.session_state.get(key, {}).get("edited_rows", {})
    view_ids = st.session_state.get("_view_ids_m2", [])
    if not changes:
        return
    for r_idx_str, cols in changes.items():
        r_idx = int(r_idx_str)
        if r_idx < len(view_ids):
            mid = view_ids[r_idx]
            for item in st.session_state.m2_assignments:
                if item["member_id"] == mid:
                    for c, val in cols.items():
                        item[c] = val
                    # Liên thông chỉ tiêu xuống Module 3-7
                    for x in st.session_state.m3_hsba:
                        if x["member_id"] == mid:
                            x["target_week"] = int(item["hsba_target_week"])
                    for x in st.session_state.m4_rx:
                        if x["member_id"] == mid:
                            x["target_out_week"] = int(item["rx_out_target_week"])
                            x["target_in_week"] = int(item["rx_in_target_week"])
                    for x in st.session_state.m5_consult:
                        if x["member_id"] == mid:
                            x["target_consult_week"] = int(item["consult_target_week"])
                    for x in st.session_state.m6_dose:
                        if x["member_id"] == mid:
                            x["target_dose_week"] = int(item["dose_target_week"])
                    for x in st.session_state.m7_counsel:
                        if x["member_id"] == mid:
                            x["target_counsel_pct"] = float(item["counsel_target_pct"])
                    break
    save_state_to_disk()


def cb_sync_module_3():
    key = f"editor_module_3_{st.session_state.editor_ver}"
    changes = st.session_state.get(key, {}).get("edited_rows", {})
    view_ids = st.session_state.get("_view_ids_m3", [])
    if not changes:
        return
    for r_idx_str, cols in changes.items():
        r_idx = int(r_idx_str)
        if r_idx < len(view_ids):
            mid = view_ids[r_idx]
            for item in st.session_state.m3_hsba:
                if item["member_id"] == mid:
                    for c, val in cols.items():
                        item[c] = int(val) if val is not None else 0
                        if c == "target_week":
                            sync_m2_target_field(mid, "hsba_target_week", int(item[c]))
                    break
    save_state_to_disk()


def cb_sync_module_4():
    key = f"editor_module_4_{st.session_state.editor_ver}"
    changes = st.session_state.get(key, {}).get("edited_rows", {})
    view_ids = st.session_state.get("_view_ids_m4", [])
    if not changes:
        return
    for r_idx_str, cols in changes.items():
        r_idx = int(r_idx_str)
        if r_idx < len(view_ids):
            mid = view_ids[r_idx]
            for item in st.session_state.m4_rx:
                if item["member_id"] == mid:
                    for c, val in cols.items():
                        item[c] = int(val) if val is not None else 0
                        if c == "target_out_week":
                            sync_m2_target_field(mid, "rx_out_target_week", int(item[c]))
                        elif c == "target_in_week":
                            sync_m2_target_field(mid, "rx_in_target_week", int(item[c]))
                    break
    save_state_to_disk()


def cb_sync_module_5():
    key = f"editor_module_5_{st.session_state.editor_ver}"
    changes = st.session_state.get(key, {}).get("edited_rows", {})
    view_ids = st.session_state.get("_view_ids_m5", [])
    if not changes:
        return
    for r_idx_str, cols in changes.items():
        r_idx = int(r_idx_str)
        if r_idx < len(view_ids):
            mid = view_ids[r_idx]
            for item in st.session_state.m5_consult:
                if item["member_id"] == mid:
                    for c, val in cols.items():
                        if c == "doctor_consensus_pct":
                            item[c] = float(val) if val is not None else 0.0
                        else:
                            item[c] = int(val) if val is not None else 0
                            if c == "target_consult_week":
                                sync_m2_target_field(mid, "consult_target_week", int(item[c]))
                    break
    save_state_to_disk()


def cb_sync_module_6():
    key = f"editor_module_6_{st.session_state.editor_ver}"
    changes = st.session_state.get(key, {}).get("edited_rows", {})
    view_ids = st.session_state.get("_view_ids_m6", [])
    if not changes:
        return
    for r_idx_str, cols in changes.items():
        r_idx = int(r_idx_str)
        if r_idx < len(view_ids):
            mid = view_ids[r_idx]
            for item in st.session_state.m6_dose:
                if item["member_id"] == mid:
                    for c, val in cols.items():
                        if c == "intervention_success_pct":
                            item[c] = float(val) if val is not None else 0.0
                        else:
                            item[c] = int(val) if val is not None else 0
                            if c == "target_dose_week":
                                sync_m2_target_field(mid, "dose_target_week", int(item[c]))
                    break
    save_state_to_disk()


def cb_sync_module_7():
    key = f"editor_module_7_{st.session_state.editor_ver}"
    changes = st.session_state.get(key, {}).get("edited_rows", {})
    view_ids = st.session_state.get("_view_ids_m7", [])
    if not changes:
        return
    for r_idx_str, cols in changes.items():
        r_idx = int(r_idx_str)
        if r_idx < len(view_ids):
            mid = view_ids[r_idx]
            for item in st.session_state.m7_counsel:
                if item["member_id"] == mid:
                    for c, val in cols.items():
                        if c == "target_counsel_pct":
                            item[c] = float(val) if val is not None else 0.0
                            sync_m2_target_field(mid, "counsel_target_pct", float(item[c]))
                        else:
                            item[c] = int(val) if val is not None else 0
                    for d_num in ["2", "3", "4", "5", "6"]:
                        if item[f"coun_t{d_num}"] > item[f"tot_t{d_num}"]:
                            item[f"tot_t{d_num}"] = item[f"coun_t{d_num}"]
                    break
    save_state_to_disk()


# Khởi tạo dữ liệu an toàn (Tự động khôi phục từ file autosave nếu có)
ensure_session_state_initialized(force_reset=False)


# ==============================================================================
# THANH BÊN (SIDEBAR): ĐIỀU KHIỂN TRỌNG SỐ KPI & ĐỒNG BỘ EXCEL (.XLSX)
# ==============================================================================
with st.sidebar:
    st.markdown("## 🧩 QUẢN TRỊ KPI CHUẨN EXCEL")
    st.caption(f"🟢 Tự động lưu lúc: **{st.session_state.get('last_saved_time', 'Mới khởi tạo')}**")

    selected_subsystem = st.multiselect(
        "Lọc theo Phân hệ Chuyên môn",
        options=SUBSYSTEMS,
        default=SUBSYSTEMS,
    )

    st.markdown("### ⚖️ Trọng số & Trần điểm KPI")
    max_score_cap = st.number_input(
        "Trần điểm tối đa mỗi tiêu chí (100 - 120):",
        min_value=100.0,
        max_value=120.0,
        value=float(st.session_state.get("max_score_cap", 100.0)),
        step=5.0,
        help="100 = Chuẩn cơ bản; 110-120 = Cho phép cộng điểm thưởng khi vượt định mức KPI tuần",
    )
    st.session_state.max_score_cap = max_score_cap

    w_cur = st.session_state.weights
    w_m3_hsba = st.slider("1. Kiểm tra HSBA Tuần (%)", 0, 50, int(w_cur["w_m3_hsba"]), 5)
    w_m4_rx = st.slider("2. Duyệt Đơn Ngoại & Nội trú (%)", 0, 50, int(w_cur["w_m4_rx"]), 5)
    w_m5_consult = st.slider("3. Hội chẩn Lâm sàng (%)", 0, 50, int(w_cur["w_m5_consult"]), 5)
    w_m6_dose = st.slider("4. Can thiệp Chỉnh liều (%)", 0, 50, int(w_cur["w_m6_dose"]), 5)
    w_m7_counsel = st.slider("5. Tư vấn Đơn / Tổng đơn (%)", 0, 50, int(w_cur["w_m7_counsel"]), 5)
    w_m2_task = st.slider("6. Công việc Phân công Tuần (%)", 0, 50, int(w_cur["w_m2_task"]), 5)

    weights_dict = {
        "w_m3_hsba": w_m3_hsba,
        "w_m4_rx": w_m4_rx,
        "w_m5_consult": w_m5_consult,
        "w_m6_dose": w_m6_dose,
        "w_m7_counsel": w_m7_counsel,
        "w_m2_task": w_m2_task,
    }
    if weights_dict != st.session_state.weights:
        st.session_state.weights = weights_dict
        save_state_to_disk()

    st.caption(f"Tổng trọng số: **{sum(weights_dict.values())}%** (tự động quy chuẩn thang 100)")


# ==============================================================================
# TÍNH TOÁN ĐIỂM SỐ TỨC THỜI CHO TỪNG MODULE & MODULE 8
# ==============================================================================
df_m3_scored = score_module_3_hsba(st.session_state.m3_hsba, max_cap=st.session_state.max_score_cap)
df_m4_scored = score_module_4_prescription(st.session_state.m4_rx, max_cap=st.session_state.max_score_cap)
df_m5_scored = score_module_5_consultation(st.session_state.m5_consult, max_cap=st.session_state.max_score_cap)
df_m6_scored = score_module_6_dose_intervention(st.session_state.m6_dose, max_cap=st.session_state.max_score_cap)
df_m7_scored = score_module_7_counseling(st.session_state.m7_counsel, max_cap=st.session_state.max_score_cap)

df_master_kpi = compute_master_kpi_module8(
    st.session_state.members,
    st.session_state.m2_assignments,
    df_m3_scored,
    df_m4_scored,
    df_m5_scored,
    df_m6_scored,
    df_m7_scored,
    st.session_state.weights,
)

# Tiếp tục phần xuất/nhập Excel ở Sidebar sau khi đã có bảng điểm mới nhất
with st.sidebar:
    st.markdown("### 📊 Xuất / Nhập File Excel (.xlsx)")
    excel_bytes = export_all_to_excel_bytes(
        df_master_kpi, df_m3_scored, df_m4_scored, df_m5_scored, df_m6_scored, df_m7_scored
    )
    if excel_bytes is not None:
        st.download_button(
            label="📥 Tải xuống File Excel 9 Sheet (.xlsx)",
            data=excel_bytes,
            file_name="he_thong_kpi_duoc_lam_sang_9_sheet.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary",
        )
    else:
        st.warning("Chưa cài thư viện `openpyxl`. Chạy `pip install openpyxl` để xuất file `.xlsx`.")

    st.download_button(
        label="⬇️ Tải xuống Bản sao lưu (.json)",
        data=json.dumps(get_current_payload(), ensure_ascii=False, indent=2),
        file_name="he_thong_kpi_duoc_lam_sang.json",
        mime="application/json",
        use_container_width=True,
    )

    uploaded_file = st.file_uploader("⬆️ Chọn file Excel (.xlsx) hoặc (.json)", type=["xlsx", "json"])
    if uploaded_file is not None:
        # Nút xác nhận nạp riêng biệt để KHÔNG bao giờ tự động ghi đè khi đang sửa bảng
        if st.button("✅ Xác nhận Nạp File vừa chọn vào Hệ thống", type="primary", use_container_width=True):
            try:
                if uploaded_file.name.lower().endswith(".xlsx"):
                    import_from_excel_file(uploaded_file)
                    st.success("Đã nạp toàn bộ các Sheet từ file Excel thành công!")
                    st.rerun()
                else:
                    loaded = json.load(uploaded_file)
                    if "members" in loaded and "m3_hsba" in loaded:
                        st.session_state.members = loaded["members"]
                        st.session_state.m2_assignments = loaded["m2_assignments"]
                        st.session_state.m3_hsba = loaded["m3_hsba"]
                        st.session_state.m4_rx = loaded["m4_rx"]
                        st.session_state.m5_consult = loaded["m5_consult"]
                        st.session_state.m6_dose = loaded["m6_dose"]
                        st.session_state.m7_counsel = loaded["m7_counsel"]
                        if "weights" in loaded:
                            st.session_state.weights = loaded["weights"]
                        st.session_state.editor_ver += 1
                        save_state_to_disk()
                        st.success("Đã khôi phục dữ liệu từ file JSON thành công!")
                        st.rerun()
            except Exception as exc:
                st.error(f"Lỗi khi đọc file: {exc}")

    st.markdown("### 🛠️ Tiện ích Tuần mới")
    if st.button("🧹 Đặt số liệu Thứ 2–Thứ 6 về 0 (Nhập tuần mới)", use_container_width=True):
        for item in st.session_state.m3_hsba:
            for d in WEEKDAYS:
                item[d] = 0
        for item in st.session_state.m4_rx:
            for c in ["out_t2", "out_t3", "out_t4", "out_t5", "out_t6", "in_t2", "in_t3", "in_t4", "in_t5", "in_t6"]:
                item[c] = 0
        for item in st.session_state.m5_consult:
            for d in WEEKDAYS:
                item[d] = 0
        for item in st.session_state.m6_dose:
            for d in WEEKDAYS:
                item[d] = 0
        for item in st.session_state.m7_counsel:
            for d_num in ["2", "3", "4", "5", "6"]:
                item[f"coun_t{d_num}"] = 0
                item[f"tot_t{d_num}"] = 0
        st.session_state.editor_ver += 1
        save_state_to_disk()
        st.rerun()

    if st.button("🔄 Khôi phục Dữ liệu Mẫu Mặc định", use_container_width=True):
        ensure_session_state_initialized(force_reset=True)
        st.rerun()


df_master_filtered = df_master_kpi[df_master_kpi["subsystem"].isin(selected_subsystem)].copy()
filtered_ids = set(df_master_filtered["id"].tolist())

# ==============================================================================
# TIÊU ĐỀ CHÍNH & BẢNG CHỈ SỐ TỔNG QUAN 6 TRỤ CỘT
# ==============================================================================
st.title("🏥 HỆ THỐNG QUẢN TRỊ, CHẤM ĐIỂM KPI - TỔ DƯỢC LÂM SÀNG")
st.markdown(
    "**Chế độ Live-Excel: Sửa bất kỳ ô nào và nhấn `Enter` hoặc `Tab`, hệ thống tự động lưu vào ổ cứng và tính lại Tổng tuần + Điểm KPI tức thì**"
)

k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1:
    st.metric(
        "M3: Bệnh án Tuần (T2–T6)",
        f"{int(df_master_filtered['done_week'].sum()):,}/{int(df_master_filtered['target_week'].sum()):,}",
        f"Điểm TB: {df_master_filtered['score_m3'].mean():.1f}",
    )
with k2:
    st.metric(
        "M4: Đơn Ngoại & Nội trú",
        f"{int(df_master_filtered['done_total_rx'].sum()):,}/{int(df_master_filtered['target_total_rx'].sum()):,}",
        f"Điểm TB: {df_master_filtered['score_m4'].mean():.1f}",
    )
with k3:
    st.metric(
        "M5: Hội chẩn Lâm sàng",
        f"{int(df_master_filtered['done_consult_week'].sum()):,}/{int(df_master_filtered['target_consult_week'].sum()):,}",
        f"Điểm TB: {df_master_filtered['score_m5'].mean():.1f}",
    )
with k4:
    st.metric(
        "M6: Can thiệp Chỉnh liều",
        f"{int(df_master_filtered['done_dose_week'].sum()):,}/{int(df_master_filtered['target_dose_week'].sum()):,}",
        f"Điểm TB: {df_master_filtered['score_m6'].mean():.1f}",
    )
with k5:
    tot_c = int(df_master_filtered["counseled_week"].sum())
    tot_rx = int(df_master_filtered["total_rx_week"].sum())
    pct_c = (tot_c / tot_rx * 100.0) if tot_rx > 0 else 0.0
    st.metric(
        "M7: Tư vấn / Tổng đơn",
        f"{tot_c:,}/{tot_rx:,} ({pct_c:.1f}%)",
        f"Điểm TB: {df_master_filtered['score_m7'].mean():.1f}",
    )
with k6:
    st.metric(
        "M8: Tổng Điểm KPI Tổ",
        f"{df_master_filtered['kpi_total'].mean():.1f} / 100",
        f"{int((df_master_filtered['kpi_rank'] == 'Xuất sắc (A+)').sum())}/{len(df_master_filtered)} đạt A+",
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
        "👥 Module 1: Hồ sơ Nhân sự",
        "🤖 Module 2: Phân công & Chỉ tiêu Tuần",
        "📁 Module 3: Hồ sơ Bệnh án (T2–T6)",
        "💊 Module 4: Duyệt Đơn Ngoại & Nội trú",
        "🩺 Module 5: Hội chẩn Lâm sàng",
        "⚖️ Module 6: Can thiệp Chỉnh liều",
        "🗣️ Module 7: Tư vấn Đơn / Tổng đơn",
        "🏆 Module 8: Tổng hợp & Xuất Excel KPI",
    ]
)

# ------------------------------------------------------------------------------
# MODULE 1: CÀI ĐẶT NHÂN SỰ, KHOA LÂM SÀNG, TÍNH CÁCH & NĂNG LỰC
# ------------------------------------------------------------------------------
with tab_m1:
    st.subheader("👥 Module 1: Cài đặt Khoa Lâm sàng, Nhóm Tính cách & Năng lực")
    st.info(
        "💡 Mọi chỉnh sửa tên, khoa phụ trách, tính cách và điểm năng lực đều được **tự động lưu ngay khi nhấn Enter**."
    )

    m1_cols = [
        "id",
        "name",
        "code_role",
        "subsystem",
        "department",
        "personality_tag",
        "skill_score",
        "sla_compliance",
        "personality",
        "competencies",
    ]
    df_m1_view = pd.DataFrame(st.session_state.members)[m1_cols].copy()
    st.session_state["_view_ids_m1"] = df_m1_view["id"].tolist()

    st.data_editor(
        df_m1_view,
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
            "sla_compliance": st.column_config.NumberColumn(
                "Tuân thủ SLA (%)", min_value=0.0, max_value=100.0, step=0.5, format="%.1f%%", width="small"
            ),
            "personality": st.column_config.TextColumn("Mô tả Tính cách chi tiết", width="large"),
            "competencies": st.column_config.TextColumn("Năng lực chuyên môn & Công cụ", width="large"),
        },
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        key=f"editor_module_1_{st.session_state.editor_ver}",
        on_change=cb_sync_module_1,
    )

    if st.button(
        "⚡ Tính lại Định mức Chỉ tiêu Tuần theo Khoa/Tính cách mới (Giữ nguyên số thực tế Thứ 2–Thứ 6 đã nhập)",
        type="primary",
        use_container_width=True,
    ):
        recalculate_targets_keep_actuals(workload_scale=1.0)
        st.session_state.editor_ver += 1
        save_state_to_disk()
        st.success("Đã cập nhật định mức chỉ tiêu tuần mà vẫn bảo toàn 100% số liệu thực tế Thứ 2 – Thứ 6!")
        st.rerun()

# ------------------------------------------------------------------------------
# MODULE 2: TỰ ĐỘNG PHÂN CÔNG CÔNG VIỆC & ĐỊNH MỨC MỤC TIÊU HÀNG TUẦN
# ------------------------------------------------------------------------------
with tab_m2:
    st.subheader("🤖 Module 2: Phân công Công việc & Định mức Mục tiêu Hàng tuần (Liên thông 2 chiều với Module 3–7)")

    col_scale, col_btn_keep, col_btn_full = st.columns([1.2, 1.4, 1.4])
    with col_scale:
        workload_scale = st.slider(
            "Hệ số tải công việc toàn viện tuần này:",
            min_value=0.5,
            max_value=1.5,
            value=1.0,
            step=0.05,
        )
    with col_btn_keep:
        st.write("")
        if st.button(
            "🎯 Cập nhật Chỉ tiêu theo Hệ số tải (Giữ nguyên số Thứ 2–Thứ 6)",
            type="primary",
            use_container_width=True,
        ):
            recalculate_targets_keep_actuals(workload_scale=workload_scale)
            st.session_state.editor_ver += 1
            save_state_to_disk()
            st.success(f"Đã cập nhật chỉ tiêu tuần với hệ số tải {workload_scale}x (giữ nguyên số thực tế)!")
            st.rerun()
    with col_btn_full:
        st.write("")
        if st.button(
            "🤖 Khởi tạo lại cả Chỉ tiêu & Số liệu Mẫu (Thứ 2–Thứ 6)",
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
            st.session_state.editor_ver += 1
            save_state_to_disk()
            st.rerun()

    df_m2_view = pd.DataFrame(st.session_state.m2_assignments)
    df_m2_view = df_m2_view[df_m2_view["member_id"].isin(filtered_ids)].copy()
    st.session_state["_view_ids_m2"] = df_m2_view["member_id"].tolist()

    st.data_editor(
        df_m2_view,
        column_config={
            "member_id": st.column_config.TextColumn("Mã TV", disabled=True, width="small"),
            "member_name": st.column_config.TextColumn("Họ và tên", disabled=True, width="medium"),
            "department": st.column_config.TextColumn("Khoa Lâm sàng", disabled=True, width="medium"),
            "personality_tag": st.column_config.TextColumn("Nhóm Tính cách", disabled=True, width="medium"),
            "skill_score": st.column_config.NumberColumn("Năng lực", disabled=True, width="small"),
            "assigned_task": st.column_config.TextColumn("Nội dung Công việc Phân công Tuần", width="large"),
            "hsba_target_week": st.column_config.NumberColumn("Chỉ tiêu HSBA/Tuần", min_value=0, max_value=1000, step=5),
            "rx_out_target_week": st.column_config.NumberColumn("Chỉ tiêu Đơn Ngoại/Tuần", min_value=0, max_value=3000, step=5),
            "rx_in_target_week": st.column_config.NumberColumn("Chỉ tiêu Đơn Nội/Tuần", min_value=0, max_value=3000, step=5),
            "consult_target_week": st.column_config.NumberColumn("Chỉ tiêu Hội chẩn/Tuần", min_value=0, max_value=500, step=1),
            "dose_target_week": st.column_config.NumberColumn("Chỉ tiêu Chỉnh liều/Tuần", min_value=0, max_value=500, step=1),
            "rx_total_week_est": None,
            "counsel_target_pct": st.column_config.NumberColumn(
                "Mục tiêu Tư vấn (%)", min_value=0.0, max_value=100.0, step=1.0, format="%.1f%%"
            ),
            "assignment_completion_pct": st.column_config.NumberColumn(
                "Điểm Hoàn thành Nhiệm vụ Tuần (%)", min_value=0.0, max_value=120.0, step=1.0, format="%.1f%%"
            ),
        },
        use_container_width=True,
        hide_index=True,
        key=f"editor_module_2_{st.session_state.editor_ver}",
        on_change=cb_sync_module_2,
    )

# ------------------------------------------------------------------------------
# MODULE 3: TIÊU CHÍ 1 — KIỂM TRA HỒ SƠ BỆNH ÁN (THỨ 2 ĐẾN THỨ 6)
# ------------------------------------------------------------------------------
with tab_m3:
    st.subheader("📁 Module 3 (Tiêu chí 1): Kiểm tra Hồ sơ Bệnh án từ Thứ 2 đến Thứ 6")
    st.caption(
        "Gõ số trực tiếp vào cột **Mục tiêu** hoặc **Thứ 2 – Thứ 6** và nhấn `Enter`, cột **Tổng HSBA Cuối tuần**, **Chênh lệch** và **Điểm Module 3** sẽ tự động tính ngay lập tức như Excel."
    )

    df_m3_view = df_m3_scored[df_m3_scored["member_id"].isin(filtered_ids)].copy()
    st.session_state["_view_ids_m3"] = df_m3_view["member_id"].tolist()

    st.data_editor(
        df_m3_view,
        column_config={
            "member_id": st.column_config.TextColumn("Mã TV", disabled=True, width="small"),
            "member_name": st.column_config.TextColumn("Họ và tên Dược sĩ", disabled=True, width="medium"),
            "department": st.column_config.TextColumn("Khoa Lâm sàng", disabled=True, width="medium"),
            "target_week": st.column_config.NumberColumn("Mục tiêu HSBA Tuần", min_value=0, max_value=1000, step=5),
            "Thứ 2": st.column_config.NumberColumn("Thứ 2", min_value=0, max_value=300, step=1),
            "Thứ 3": st.column_config.NumberColumn("Thứ 3", min_value=0, max_value=300, step=1),
            "Thứ 4": st.column_config.NumberColumn("Thứ 4", min_value=0, max_value=300, step=1),
            "Thứ 5": st.column_config.NumberColumn("Thứ 5", min_value=0, max_value=300, step=1),
            "Thứ 6": st.column_config.NumberColumn("Thứ 6", min_value=0, max_value=300, step=1),
            "done_week": st.column_config.NumberColumn("Tổng HSBA Cuối tuần", disabled=True),
            "diff_week": st.column_config.NumberColumn("Chênh lệch (+/-)", disabled=True),
            "completion_pct": st.column_config.NumberColumn("Đạt Mục tiêu (%)", disabled=True, format="%.1f%%"),
            "score_m3": st.column_config.ProgressColumn(
                "Điểm Module 3", min_value=0, max_value=float(st.session_state.max_score_cap), format="%.1f đ"
            ),
        },
        use_container_width=True,
        hide_index=True,
        key=f"editor_module_3_{st.session_state.editor_ver}",
        on_change=cb_sync_module_3,
    )

    st.markdown(
        f"**📊 Dòng Tổng cộng Excel (Module 3):** Mục tiêu tuần: `{int(df_m3_view['target_week'].sum()):,}` | "
        f"Thứ 2: `{int(df_m3_view['Thứ 2'].sum()):,}` | Thứ 3: `{int(df_m3_view['Thứ 3'].sum()):,}` | "
        f"Thứ 4: `{int(df_m3_view['Thứ 4'].sum()):,}` | Thứ 5: `{int(df_m3_view['Thứ 5'].sum()):,}` | "
        f"Thứ 6: `{int(df_m3_view['Thứ 6'].sum()):,}` | **Tổng thực hiện: `{int(df_m3_view['done_week'].sum()):,}`** | "
        f"**Điểm TB Module 3: `{df_m3_view['score_m3'].mean():.1f}`**"
    )

# ------------------------------------------------------------------------------
# MODULE 4: TIÊU CHÍ 2 — DUYỆT ĐƠN THUỐC NGOẠI TRÚ & NỘI TRÚ HÀNG NGÀY
# ------------------------------------------------------------------------------
with tab_m4:
    st.subheader("💊 Module 4 (Tiêu chí 2): Duyệt Đơn thuốc Ngoại trú & Nội trú Hàng ngày (Thứ 2 – Thứ 6)")
    st.caption(
        "Hỗ trợ nhập `Mục tiêu = 0` đối với Dược sĩ chỉ phụ trách Nội trú hoặc chỉ phụ trách Ngoại trú (tự động tính 100% trọng số vào loại đơn được phân công)."
    )

    df_m4_view = df_m4_scored[df_m4_scored["member_id"].isin(filtered_ids)].copy()
    st.session_state["_view_ids_m4"] = df_m4_view["member_id"].tolist()

    st.data_editor(
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
                "done_total_rx",
                "score_m4",
            ]
        ],
        column_config={
            "member_id": st.column_config.TextColumn("Mã TV", disabled=True, width="small"),
            "member_name": st.column_config.TextColumn("Họ và tên", disabled=True, width="medium"),
            "department": st.column_config.TextColumn("Khoa Lâm sàng", disabled=True, width="medium"),
            "target_out_week": st.column_config.NumberColumn("Mục tiêu Ngoại/Tuần", min_value=0, max_value=3000),
            "out_t2": st.column_config.NumberColumn("Ngoại T2", min_value=0, max_value=1000),
            "out_t3": st.column_config.NumberColumn("Ngoại T3", min_value=0, max_value=1000),
            "out_t4": st.column_config.NumberColumn("Ngoại T4", min_value=0, max_value=1000),
            "out_t5": st.column_config.NumberColumn("Ngoại T5", min_value=0, max_value=1000),
            "out_t6": st.column_config.NumberColumn("Ngoại T6", min_value=0, max_value=1000),
            "done_out_week": st.column_config.NumberColumn("Tổng Ngoại", disabled=True),
            "target_in_week": st.column_config.NumberColumn("Mục tiêu Nội/Tuần", min_value=0, max_value=3000),
            "in_t2": st.column_config.NumberColumn("Nội T2", min_value=0, max_value=1000),
            "in_t3": st.column_config.NumberColumn("Nội T3", min_value=0, max_value=1000),
            "in_t4": st.column_config.NumberColumn("Nội T4", min_value=0, max_value=1000),
            "in_t5": st.column_config.NumberColumn("Nội T5", min_value=0, max_value=1000),
            "in_t6": st.column_config.NumberColumn("Nội T6", min_value=0, max_value=1000),
            "done_in_week": st.column_config.NumberColumn("Tổng Nội", disabled=True),
            "done_total_rx": st.column_config.NumberColumn("Tổng Đơn Duyệt", disabled=True),
            "score_m4": st.column_config.ProgressColumn(
                "Điểm Module 4", min_value=0, max_value=float(st.session_state.max_score_cap), format="%.1f đ"
            ),
        },
        use_container_width=True,
        hide_index=True,
        key=f"editor_module_4_{st.session_state.editor_ver}",
        on_change=cb_sync_module_4,
    )

    st.markdown(
        f"**📊 Dòng Tổng cộng Excel (Module 4):** Tổng Đơn Ngoại trú: `{int(df_m4_view['done_out_week'].sum()):,}/{int(df_m4_view['target_out_week'].sum()):,}` | "
        f"Tổng Đơn Nội trú: `{int(df_m4_view['done_in_week'].sum()):,}/{int(df_m4_view['target_in_week'].sum()):,}` | "
        f"**Tổng Đơn Duyệt Tuần: `{int(df_m4_view['done_total_rx'].sum()):,}`** | "
        f"**Điểm TB Module 4: `{df_m4_view['score_m4'].mean():.1f}`**"
    )

    if st.button("🔗 Đồng bộ Tổng đơn duyệt (Ngoại + Nội) từng ngày sang Tổng đơn của Module 7"):
        rx_map = {item["member_id"]: item for item in st.session_state.m4_rx}
        for item7 in st.session_state.m7_counsel:
            mid = item7["member_id"]
            if mid in rx_map:
                r4 = rx_map[mid]
                for d_num in ["2", "3", "4", "5", "6"]:
                    tot_day = int(r4[f"out_t{d_num}"]) + int(r4[f"in_t{d_num}"])
                    item7[f"tot_t{d_num}"] = max(tot_day, int(item7[f"coun_t{d_num}"]))
        st.session_state.editor_ver += 1
        save_state_to_disk()
        st.success("Đã đồng bộ Tổng đơn (Ngoại + Nội) từ Module 4 sang cột Tổng đơn từng ngày của Module 7!")
        st.rerun()

# ------------------------------------------------------------------------------
# MODULE 5: TIÊU CHÍ 3 — HỘI CHẨN LÂM SÀNG HÀNG NGÀY
# ------------------------------------------------------------------------------
with tab_m5:
    st.subheader("🩺 Module 5 (Tiêu chí 3): Hội chẩn Lâm sàng Hàng ngày (Thứ 2 – Thứ 6)")
    st.caption(
        "Công thức chuẩn Excel: **Điểm Module 5 = 65% × (% Hoàn thành số lượng hội chẩn) + 35% × (% Bác sĩ đồng thuận)** (nếu số ca thực hiện = 0 khi có giao chỉ tiêu thì điểm = 0)."
    )

    df_m5_view = df_m5_scored[df_m5_scored["member_id"].isin(filtered_ids)].copy()
    st.session_state["_view_ids_m5"] = df_m5_view["member_id"].tolist()

    st.data_editor(
        df_m5_view,
        column_config={
            "member_id": st.column_config.TextColumn("Mã TV", disabled=True, width="small"),
            "member_name": st.column_config.TextColumn("Họ và tên Dược sĩ", disabled=True, width="medium"),
            "department": st.column_config.TextColumn("Khoa Lâm sàng", disabled=True, width="medium"),
            "target_consult_week": st.column_config.NumberColumn(
                "Mục tiêu Ca Hội chẩn/Tuần", min_value=0, max_value=500, step=1
            ),
            "Thứ 2": st.column_config.NumberColumn("HC Thứ 2", min_value=0, max_value=100),
            "Thứ 3": st.column_config.NumberColumn("HC Thứ 3", min_value=0, max_value=100),
            "Thứ 4": st.column_config.NumberColumn("HC Thứ 4", min_value=0, max_value=100),
            "Thứ 5": st.column_config.NumberColumn("HC Thứ 5", min_value=0, max_value=100),
            "Thứ 6": st.column_config.NumberColumn("HC Thứ 6", min_value=0, max_value=100),
            "done_consult_week": st.column_config.NumberColumn("Tổng Ca Hội chẩn", disabled=True),
            "consult_qty_pct": st.column_config.NumberColumn("Đạt Số lượng (%)", disabled=True, format="%.1f%%"),
            "doctor_consensus_pct": st.column_config.NumberColumn(
                "BS Đồng thuận Hội chẩn (%)", min_value=0.0, max_value=100.0, step=0.5, format="%.1f%%"
            ),
            "score_m5": st.column_config.ProgressColumn(
                "Điểm Module 5", min_value=0, max_value=float(st.session_state.max_score_cap), format="%.1f đ"
            ),
        },
        use_container_width=True,
        hide_index=True,
        key=f"editor_module_5_{st.session_state.editor_ver}",
        on_change=cb_sync_module_5,
    )

    st.markdown(
        f"**📊 Dòng Tổng cộng Excel (Module 5):** Tổng ca Hội chẩn: `{int(df_m5_view['done_consult_week'].sum()):,}/{int(df_m5_view['target_consult_week'].sum()):,}` | "
        f"Tỷ lệ BS đồng thuận TB: `{df_m5_view['doctor_consensus_pct'].mean():.1f}%` | "
        f"**Điểm TB Module 5: `{df_m5_view['score_m5'].mean():.1f}`**"
    )

# ------------------------------------------------------------------------------
# MODULE 6: TIÊU CHÍ 4 — CAN THIỆP CHỈNH LIỀU TRÊN LÂM SÀNG HÀNG NGÀY
# ------------------------------------------------------------------------------
with tab_m6:
    st.subheader("⚖️ Module 6 (Tiêu chí 4): Can thiệp Chỉnh liều trên Lâm sàng Hàng ngày (Thứ 2 – Thứ 6)")
    st.caption(
        "Công thức chuẩn Excel: **Điểm Module 6 = 65% × (% Hoàn thành số ca chỉnh liều) + 35% × (% Can thiệp chỉnh liều thành công)**."
    )

    df_m6_view = df_m6_scored[df_m6_scored["member_id"].isin(filtered_ids)].copy()
    st.session_state["_view_ids_m6"] = df_m6_view["member_id"].tolist()

    st.data_editor(
        df_m6_view,
        column_config={
            "member_id": st.column_config.TextColumn("Mã TV", disabled=True, width="small"),
            "member_name": st.column_config.TextColumn("Họ và tên Dược sĩ", disabled=True, width="medium"),
            "department": st.column_config.TextColumn("Khoa Lâm sàng", disabled=True, width="medium"),
            "target_dose_week": st.column_config.NumberColumn(
                "Mục tiêu Ca Chỉnh liều/Tuần", min_value=0, max_value=500, step=1
            ),
            "Thứ 2": st.column_config.NumberColumn("CL Thứ 2", min_value=0, max_value=100),
            "Thứ 3": st.column_config.NumberColumn("CL Thứ 3", min_value=0, max_value=100),
            "Thứ 4": st.column_config.NumberColumn("CL Thứ 4", min_value=0, max_value=100),
            "Thứ 5": st.column_config.NumberColumn("CL Thứ 5", min_value=0, max_value=100),
            "Thứ 6": st.column_config.NumberColumn("CL Thứ 6", min_value=0, max_value=100),
            "done_dose_week": st.column_config.NumberColumn("Tổng Ca Chỉnh liều", disabled=True),
            "dose_qty_pct": st.column_config.NumberColumn("Đạt Số lượng (%)", disabled=True, format="%.1f%%"),
            "intervention_success_pct": st.column_config.NumberColumn(
                "Tỷ lệ Chỉnh liều Thành công (%)", min_value=0.0, max_value=100.0, step=0.5, format="%.1f%%"
            ),
            "score_m6": st.column_config.ProgressColumn(
                "Điểm Module 6", min_value=0, max_value=float(st.session_state.max_score_cap), format="%.1f đ"
            ),
        },
        use_container_width=True,
        hide_index=True,
        key=f"editor_module_6_{st.session_state.editor_ver}",
        on_change=cb_sync_module_6,
    )

    st.markdown(
        f"**📊 Dòng Tổng cộng Excel (Module 6):** Tổng ca Chỉnh liều: `{int(df_m6_view['done_dose_week'].sum()):,}/{int(df_m6_view['target_dose_week'].sum()):,}` | "
        f"Tỷ lệ thành công TB: `{df_m6_view['intervention_success_pct'].mean():.1f}%` | "
        f"**Điểm TB Module 6: `{df_m6_view['score_m6'].mean():.1f}`**"
    )

# ------------------------------------------------------------------------------
# MODULE 7: TIÊU CHÍ 5 — TƯ VẤN ĐƠN THUỐC TRÊN TỔNG SỐ ĐƠN TRONG NGÀY
# ------------------------------------------------------------------------------
with tab_m7:
    st.subheader("🗣️ Module 7 (Tiêu chí 5): Tư vấn Đơn thuốc trên Tổng số Đơn thuốc trong Ngày (Thứ 2 – Thứ 6)")
    st.caption(
        "Công thức chuẩn Excel: **Tỷ lệ Tư vấn Thực tế (%) = (Tổng đơn tư vấn tuần / Tổng đơn tuần) × 100%**, đối chiếu với **Mục tiêu Tỷ lệ Tư vấn (%)**."
    )

    df_m7_view = df_m7_scored[df_m7_scored["member_id"].isin(filtered_ids)].copy()
    st.session_state["_view_ids_m7"] = df_m7_view["member_id"].tolist()

    st.data_editor(
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
                "Mục tiêu Tỷ lệ Tư vấn (%)", min_value=0.0, max_value=100.0, step=1.0, format="%.1f%%"
            ),
            "coun_t2": st.column_config.NumberColumn("Tư vấn T2", min_value=0, max_value=2000),
            "tot_t2": st.column_config.NumberColumn("Tổng đơn T2", min_value=0, max_value=2000),
            "coun_t3": st.column_config.NumberColumn("Tư vấn T3", min_value=0, max_value=2000),
            "tot_t3": st.column_config.NumberColumn("Tổng đơn T3", min_value=0, max_value=2000),
            "coun_t4": st.column_config.NumberColumn("Tư vấn T4", min_value=0, max_value=2000),
            "tot_t4": st.column_config.NumberColumn("Tổng đơn T4", min_value=0, max_value=2000),
            "coun_t5": st.column_config.NumberColumn("Tư vấn T5", min_value=0, max_value=2000),
            "tot_t5": st.column_config.NumberColumn("Tổng đơn T5", min_value=0, max_value=2000),
            "coun_t6": st.column_config.NumberColumn("Tư vấn T6", min_value=0, max_value=2000),
            "tot_t6": st.column_config.NumberColumn("Tổng đơn T6", min_value=0, max_value=2000),
            "counseled_week": st.column_config.NumberColumn("Tổng Đơn Tư vấn", disabled=True),
            "total_rx_week": st.column_config.NumberColumn("Tổng Đơn Tuần", disabled=True),
            "actual_counsel_pct": st.column_config.NumberColumn("Tỷ lệ Thực tế (%)", disabled=True, format="%.1f%%"),
            "score_m7": st.column_config.ProgressColumn(
                "Điểm Module 7", min_value=0, max_value=float(st.session_state.max_score_cap), format="%.1f đ"
            ),
        },
        use_container_width=True,
        hide_index=True,
        key=f"editor_module_7_{st.session_state.editor_ver}",
        on_change=cb_sync_module_7,
    )

    st.markdown(
        f"**📊 Dòng Tổng cộng Excel (Module 7):** Tổng đơn được tư vấn: `{int(df_m7_view['counseled_week'].sum()):,}/{int(df_m7_view['total_rx_week'].sum()):,}` | "
        f"**Điểm TB Module 7: `{df_m7_view['score_m7'].mean():.1f}`**"
    )

# ------------------------------------------------------------------------------
# MODULE 8: TỔNG HỢP & TÍNH KPI TOÀN DIỆN TỪ TẤT CẢ CÁC MODULE
# ------------------------------------------------------------------------------
with tab_m8:
    st.subheader("🏆 Module 8: Bảng Tổng hợp Điểm Tất cả Tiêu chí & Đánh giá KPI Cuối tuần")
    w = st.session_state.weights
    st.markdown(
        f"**Trọng số hiện hành:** M3 (HSBA): `{w['w_m3_hsba']}%` • M4 (Duyệt đơn): `{w['w_m4_rx']}%` • "
        f"M5 (Hội chẩn): `{w['w_m5_consult']}%` • M6 (Chỉnh liều): `{w['w_m6_dose']}%` • "
        f"M7 (Tư vấn): `{w['w_m7_counsel']}%` • M2 (Nhiệm vụ phân công): `{w['w_m2_task']}%`"
    )

    df_kpi_sorted = df_master_filtered.sort_values(by="kpi_total", ascending=False).copy()

    st.dataframe(
        df_kpi_sorted[
            [
                "id",
                "name",
                "department",
                "done_week",
                "score_m3",
                "done_total_rx",
                "score_m4",
                "done_consult_week",
                "score_m5",
                "done_dose_week",
                "score_m6",
                "actual_counsel_pct",
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
            "done_week": st.column_config.NumberColumn("Số HSBA"),
            "score_m3": st.column_config.NumberColumn("Điểm M3", format="%.1f"),
            "done_total_rx": st.column_config.NumberColumn("Số Đơn duyệt"),
            "score_m4": st.column_config.NumberColumn("Điểm M4", format="%.1f"),
            "done_consult_week": st.column_config.NumberColumn("Ca Hội chẩn"),
            "score_m5": st.column_config.NumberColumn("Điểm M5", format="%.1f"),
            "done_dose_week": st.column_config.NumberColumn("Ca Chỉnh liều"),
            "score_m6": st.column_config.NumberColumn("Điểm M6", format="%.1f"),
            "actual_counsel_pct": st.column_config.NumberColumn("% Tư vấn", format="%.1f%%"),
            "score_m7": st.column_config.NumberColumn("Điểm M7", format="%.1f"),
            "assignment_completion_pct": st.column_config.NumberColumn("Điểm M2", format="%.1f"),
            "kpi_total": st.column_config.ProgressColumn(
                "TỔNG ĐIỂM KPI", min_value=0, max_value=float(st.session_state.max_score_cap), format="%.1f đ"
            ),
            "kpi_rank": "Xếp loại KPI",
        },
        use_container_width=True,
        hide_index=True,
    )

    col_dl_xlsx, col_dl_csv = st.columns(2)
    with col_dl_xlsx:
        if excel_bytes is not None:
            st.download_button(
                label="📥 Xuất Toàn bộ 9 Sheet ra File Excel (.xlsx)",
                data=excel_bytes,
                file_name="he_thong_kpi_duoc_lam_sang_9_sheet.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True,
            )
    with col_dl_csv:
        csv_master = df_kpi_sorted.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 Xuất Bảng Tổng hợp KPI (Module 8) ra CSV",
            data=csv_master,
            file_name="bang_kpi_tong_hop_module8.csv",
            mime="text/csv",
            use_container_width=True,
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
