
# PDP Integration Studio 2.0
Ứng dụng tiếng Việt hỗ trợ giáo viên Toán lớp 5 (Kết nối tri thức) thiết kế nhiệm vụ tích hợp năng lực **Tính chủ động và tự định hướng (INI&SED)**.

## Luồng làm việc
- V1: bảng tham chiếu 8 cột cho một bài học. Không tích hợp là một lựa chọn hợp lệ.
- V2: kế hoạch bài dạy từ V1 tích hợp đã duyệt; máy chủ kiểm tra liên kết, YCCĐ và chỉ báo.
- V3: dự án có tiến trình, sản phẩm, minh chứng và đánh giá.
- V4: đề mẫu gắn nhật ký phản tư trước–trong–sau. Đây là thiết kế mới phát triển từ tiêu đề V4 trong tài liệu gốc, chưa phải đặc tả đã được nhà trường phê chuẩn.
- Mỗi bài chọn 1–2 mã; rubric lớp 5 lấy nguyên mô tả 4 mức từ TH_INI&SED.xlsx.
- Bản AI luôn là nháp. Kiểm tra cấu trúc không xác nhận chất lượng sư phạm. Duyệt cần mã quản lý, người duyệt, nhận xét và xác nhận đối chiếu nguồn.
- Chỉnh sửa, duyệt đều tạo phiên bản bất biến mới. Ví dụ minh họa không được duyệt chính thức.
- Xuất Word, Excel và PDF đủ các mục, rubric, nguồn và dấu vết duyệt; PDF có phông Unicode.

## Nguồn và giới hạn
Gói cũ có 97 đoạn từ 12 tài liệu. Bản mới dùng 15 đoạn nguồn khung/PPCT và 9 rubric lớp 5 đã chuẩn hóa; bỏ các bài demo khỏi luồng lấy nguồn. Các PDF CTGDPT Toán và SGK Toán 5 tập 1/2 có 0 đoạn. Không dùng bài mẫu như nguồn chính thức của YCCĐ; mỗi bản cần giáo viên bổ sung đoạn nguồn và vị trí, rồi đối chiếu khi duyệt. Cơ chế lấy nguồn ưu tiên nguồn khung/PPCT, rubric của mã đã chọn được cung cấp bắt buộc. Tệp PDF scan cần OCR bên ngoài.
Phiên bản này tập trung Toán lớp 5, chưa hỗ trợ mọi môn/lớp. Không chấm mức năng lực học sinh tự động. V1 hiện tạo cho từng bài, có thể lặp lại bài 10–33, chưa sinh cả 24 bài trong một lượt.

## Vận hành
Mã nguồn FastAPI ở app.py; không giải nén ứng dụng lúc chạy.
Tài liệu nguồn không nằm trong kho GitHub công khai. PDP_KNOWLEDGE_JSON chứa corpus, rubrics và manifest trong cấu hình riêng của dự án Vercel. Khi chạy local cần có các tệp nguồn đã được cấp quyền trong data/ hoặc biến này.
Các biến máy chủ:
OPENAI_API_KEY (dùng khóa hiện có), OPENAI_MODEL (giữ lựa chọn hiện có), BLOB_READ_WRITE_TOKEN (private Vercel Blob), PDP_SESSION_SECRET (ngẫu nhiên), PDP_REVIEW_CODE (mã người duyệt).
MOCK_AI cũ không được dùng. Thiếu khóa thì báo chưa kết nối, không âm thầm dùng kết quả giả.
Lưu trữ private Blob, thư mục tách theo cookie không gian có chữ ký, HttpOnly/SameSite strict. Không xuất token/khóa ra trình duyệt. Cookie là quyền truy cập không gian trên thiết bị; xóa cookie sẽ mất đường truy cập, nên xuất tài liệu làm bản sao. Chưa có tài khoản cá nhân, đồng bộ thiết bị hoặc phân quyền theo trường. Mã duyệt xác nhận quyền, tên người duyệt tự khai báo. Giới hạn tần suất trong bộ nhớ chỉ bảo vệ từng tiến trình; cần giải pháp chia sẻ hạn mức cho triển khai công cộng nhiều người.
Local: pip install -r requirements.txt; uvicorn app:app --port 8765. Dữ liệu local nằm trong .local-data, không đưa vào Git. Vercel thiếu storage/secret sẽ báo lỗi thay vì giả lưu vào ổ tạm.
Kiểm tra: pytest tests -q. Bao gồm hồi quy bảng rỗng/mã lạ/minh chứng đơn nguồn, quyền không gian, phiên bản duyệt, V1→V2, xuất Unicode và nguồn bổ sung.
