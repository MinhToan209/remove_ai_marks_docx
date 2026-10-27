# remove_ai_marks_docx

Công cụ Python nhỏ để làm sạch một số **metadata** và ký tự Unicode vô hình trong file Microsoft Word `.docx`.

> Công cụ này dành cho tài liệu do bạn sở hữu hoặc được phép xử lý. Nó không chứng minh tài liệu do con người viết và không loại bỏ được mọi dạng watermark thống kê hoặc dấu hiệu của AI detector.

## Tính năng

- Xóa giá trị metadata trong `docProps/core.xml` và `docProps/app.xml`, gồm author, title, company, application và các thuộc tính tương tự.
- Xóa custom properties trong `docProps/custom.xml`.
- Xóa một số ký tự điều khiển/Unicode vô hình thường gặp khỏi các phần XML của DOCX.
- Ghi ra file mới; file gốc không bị thay đổi.
- Chỉ dùng Python standard library, không cần cài package ngoài.

## Yêu cầu

- Python 3.9 trở lên
- File Word định dạng `.docx`

## Cài đặt

```bash
git clone https://github.com/MinhToan209/remove_ai_marks_docx.git
cd remove_ai_marks_docx
```

## Cách dùng

```bash
python3 remove_ai_marks_docx.py input.docx output.docx
```

Ví dụ:

```bash
python3 remove_ai_marks_docx.py \
  "./document.docx" \
  "./document.cleaned.docx"
```

Sau khi chạy, chương trình sẽ báo số ký tự vô hình đã xóa và các phần DOCX đã xử lý.

## Kiểm tra kết quả trong Word

Mở file output bằng Microsoft Word và kiểm tra lại:

1. **File → Info → Check for Issues → Inspect Document**
2. Chọn các mục cần kiểm tra.
3. Lưu một bản sao nếu cần tiếp tục chỉnh sửa.

## Giới hạn

- Không rewrite nội dung văn bản.
- Không xóa chắc chắn được watermark hình ảnh, C2PA soft binding, audio/video watermark hoặc watermark thống kê trong văn phong.
- Không tự động xóa tracked changes, comments hoặc embedded files.
- Với tài liệu quan trọng, luôn giữ file gốc và kiểm tra lại bố cục, chữ ký số, liên kết, hình ảnh và metadata sau khi xử lý.

## License

MIT
