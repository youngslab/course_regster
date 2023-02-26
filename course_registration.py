from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from automatic import browser

import os
import time
from enum import Enum

is_testing = False


def create_driver(headless=False):
    options = webdriver.EdgeOptions()
    # level 3 is lowest value for log-level
    options.add_argument('log-level=3')
    if headless:
        options.add_argument('headless')
        options.add_argument('disable-gpu')
    service = Service(EdgeChromiumDriverManager().install())
    return webdriver.Edge(options=options, service=service)


def is_application_period(context):
    preiod = browser.Element(
        context, by="xpath", path="//p[text()='신청기간이 아닙니다.']")
    return not preiod.exist(timeout=1)


class Category(Enum):
    MON = "1.월요부서"
    TUE = "2.화요부서"
    WED = "3.수요부서"
    THU = "4.목요부서"
    FRI = "5.금요부서"
    COM = "7.컴퓨터"
    ETC = "8.수학,주산,체스"


# 23' 박하얀 방과후 수업
classes = [(Category.ETC, "주산암산A"), (Category.FRI, "로봇B"), (Category.ETC, "체스A"),
           (Category.MON, "요리체험A")]

joy_url = 'https://www.afteredu.kr/register/info.asp?School_id=120023&uKey=06877C6'

hani_url = 'https://w2.afteredu.kr/register/info.asp?School_id=120023&uKey=13A331B'

if __name__ == "__main__":
    driver = create_driver()
    context = browser.Context(driver, hani_url, default_timeout=10)

    while not is_application_period(context) and not is_testing:
        print("수강신청 기간이 아닙니다.")
        time.sleep(0.5)
        context.refresh()

    for cls in classes:
        cat: Category = cls[0]
        name = cls[1]

        # 수강신청 페이지로 이동
        context.set_url(
            f"https://www.afteredu.kr/register/subscribe1.asp?school_id=120023&subject_do={cat.value}&inning=2023-1&ukey=06877C6")

        # 강좌 등록버튼 클릭
        btn = browser.ClickableElement(context, by="xpath",
                                       path=f"//*[contains(text(), '{name}')]/../../../div[2]/span[2]/a")
        ok = btn.click()

        # 팝업이 생기면 확인버튼
        #  - 만약 없다면? 만약 3초동안 popup이 없다면 그냥 진행
        alert = browser.Alert(context)
        print(f"Accept popup: \"{alert.text()}\"")
        alert.accept("", timeout=1)

        # 결과 출력
        print(f"수강신청 {'성공' if ok else '실패'}: 영역={cat}, 이름={name}")


    # Category 선택

    print(f"press the enter key.")
    input()
