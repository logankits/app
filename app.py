import streamlit as st
import pandas as pd
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

# Initialize session state
df_key = "product_list"
if df_key not in st.session_state:
    st.session_state[df_key] = []

st.set_page_config(page_title="Quản lý sản phẩm", layout="centered")
st.title("📦 Quản lý sản phẩm")

# --- Form nhập liệu ---
with st.form("product_form"):
    col1, col2 = st.columns([2, 1])
    name = col1.text_input("Tên sản phẩm")
    price = col2.text_input("Giá tiền (VNĐ)")
    submitted = st.form_submit_button("➕ Thêm")

    if submitted:
        if name and price:
            try:
                price_float = float(price)
                st.session_state[df_key].append({"name": name, "price": price_float})
                st.success("✅ Đã thêm sản phẩm!")
            except:
                st.error("❌ Giá tiền phải là số!")
        else:
            st.warning("⚠️ Nhập đủ tên và giá!")

# --- Bảng danh sách ---
data = st.session_state[df_key]

if data:
    df = pd.DataFrame(data)
    df.index += 1
    df_display = df.copy()
    df_display["price"] = df_display["price"].apply(lambda x: f"{int(x):,}".replace(",", ".") + ".000")
    st.write("### 📄 Danh sách sản phẩm")
    edited_df = st.data_editor(df_display, use_container_width=True, key="editor")

    # Cập nhật thay đổi trực tiếp
    try:
        for i in edited_df.index:
            raw_price = edited_df.loc[i, "price"].replace(".000", "").replace(".", "")
            st.session_state[df_key][i - 1]["name"] = edited_df.loc[i, "name"]
            st.session_state[df_key][i - 1]["price"] = float(raw_price)
    except:
        pass

    if st.button("🗑️ Xoá toàn bộ"):
        st.session_state[df_key] = []
        st.success("✅ Đã xoá hết danh sách!")

    # --- Xuất Excel ---
    def export_to_excel():
        wb = Workbook()
        ws = wb.active
        ws.title = "Sản phẩm"
        ws.append(["STT", "Tên sản phẩm", "Giá tiền (VNĐ)"])

        for i, item in enumerate(st.session_state[df_key], 1):
            ws.append([i, item["name"], int(item["price"])*1000])

        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal="center")

        for col in ws.columns:
            max_length = max(len(str(cell.value)) for cell in col if cell.value)
            ws.column_dimensions[col[0].column_letter].width = max_length + 4

        buffer = BytesIO()
        wb.save(buffer)
        return buffer.getvalue()

    st.download_button(
        label="📤 Tải về Excel",
        data=export_to_excel(),
        file_name="danh_sach_san_pham.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("📢 Chưa có sản phẩm nào.")