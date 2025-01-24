import os
import tkinter as tk
from tkinter import filedialog, messagebox
from ebooklib import epub
from bs4 import BeautifulSoup


# 1. EPUB 파일 읽기
def read_epub(file_path):
    return epub.read_epub(file_path)


# 2. 본문 제목과 목차 수정하기
def update_titles_and_toc(book, first_chapter_option, start_from_first, next_chapter_number):
    items = list(book.get_items())
    chapter_number = next_chapter_number
    first_chapter_done = False  # 첫 번째 화수 처리 여부

    # 2.1. 본문 제목 수정
    for item in items:
        if isinstance(item, epub.EpubHtml):  # EpubHtml 객체만 처리
            soup = BeautifulSoup(item.get_body_content(), 'html.parser')

            headers = soup.find_all(['h1', 'h2', 'h3'])  # 제목 찾기
            for header in headers:
                original_title = header.string  # 기존 제목을 보존

                if not first_chapter_done:
                    # 첫 번째 제목 처리
                    if first_chapter_option == "프롤로그":
                        header.string = f"프롤로그.  {original_title}"
                    elif first_chapter_option == "공백":
                        header.string = original_title  # 아무 것도 추가하지 않음
                    else:
                        header.string = f"{first_chapter_option} {original_title}"
                    first_chapter_done = True
                else:
                    # 두 번째 제목부터는 N화 추가
                    header.string = f"{chapter_number}화. {original_title}"
                    chapter_number += 1

            # 수정된 내용을 본문에 반영
            item.set_content(str(soup))

    # 2.2. 목차 제목 수정
    new_toc = []
    chapter_number = next_chapter_number
    first_chapter_done = False

    for toc_item in book.toc:
        original_title = toc_item.title

        if not first_chapter_done:
            # 첫 번째 목차 제목 처리
            if first_chapter_option == "프롤로그":
                toc_item.title = f"프롤로그.  {original_title}"
            elif first_chapter_option == "공백":
                toc_item.title = original_title  # 아무 것도 추가하지 않음
            else:
                toc_item.title = f"{first_chapter_option} {original_title}"
            first_chapter_done = True
        else:
            # 두 번째 목차 제목부터는 N화 추가
            toc_item.title = f"{chapter_number}화. {original_title}"
            chapter_number += 1

        new_toc.append(toc_item)

    book.toc = new_toc  # 목차를 업데이트

    return book


# 3. 파일 저장
def save_book_as(book, save_path):
    epub.write_epub(save_path, book)


# 4. 옵션 선택 창
def get_user_input(file_path):
    def submit():
        first_chapter_option = first_chapter_var.get()
        start_from_first = start_from_first_var.get()
        next_chapter_number = 2 if start_from_first == "2" else 1

        # EPUB 파일 읽기 및 수정
        book = read_epub(file_path)
        updated_book = update_titles_and_toc(book, first_chapter_option, start_from_first, next_chapter_number)

        # 저장 경로 선택
        save_path = filedialog.asksaveasfilename(defaultextension=".epub", filetypes=[("EPUB files", "*.epub")])
        if save_path:
            save_book_as(updated_book, save_path)
            messagebox.showinfo("완료", "파일이 성공적으로 저장되었습니다!")
        else:
            messagebox.showinfo("취소", "저장이 취소되었습니다.")
        window.destroy()

    # 옵션 UI 구성
    window = tk.Tk()
    window.title("EPUB 화수 추가 옵션 선택")

    tk.Label(window, text="첫 번째 목차 제목에 추가할 내용:").pack(pady=5)
    first_chapter_var = tk.StringVar(value="프롤로그")
    tk.OptionMenu(window, first_chapter_var, "프롤로그", "공백", "1화").pack()

    tk.Label(window, text="두 번째 목차부터 시작할 화수:").pack(pady=5)
    start_from_first_var = tk.StringVar(value="1")
    tk.OptionMenu(window, start_from_first_var, "1", "2").pack()

    tk.Button(window, text="확인", command=submit).pack(pady=10)
    window.mainloop()



# 5. 줄 정리 (각 문단 사이에 두 줄씩 추가)
def clean_paragraph_spacing(book):
    for item in book.get_items():
        if isinstance(item, epub.EpubHtml):  # HTML 본문만 처리
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            paragraphs = soup.find_all('p')

            # 각 문단 사이에 두 줄을 추가하기 위한 텍스트로 변환
            new_content = ""
            for paragraph in paragraphs:
                # 각 문단 뒤에 두 줄 공백 추가 (빈 <p> 태그 두 개 추가)
                new_content += str(paragraph) + "<p> </p><p> </p>"

            # 변경 사항 저장
            item.set_content(new_content)

    return book

# 6. 프로그램 실행
def main():
    # 파일 선택
    file_path = filedialog.askopenfilename(filetypes=[("EPUB files", "*.epub")])
    if not file_path:
        messagebox.showinfo("알림", "파일을 선택하지 않았습니다.")
        return

    # 사용자 입력 받기
    get_user_input(file_path)


if __name__ == "__main__":
    main()
