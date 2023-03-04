from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from automatic import browser

import os
import time
from enum import Enum

# To get argument
import argparse


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



# children = dict()
table = {
    "hani": {
        "url": "https://www.afteredu.kr/register/info.asp?School_id=120023&uKey=13A331B",
        "classes": [(Category.FRI, "아나운서&성우교실A"), (Category.ETC, "체스A")],
        "key": "13A331B"
    },
    "joy": {
        "url": "https://www.afteredu.kr/register/info.asp?School_id=120023&uKey=06877C6",
        "classes": [(Category.COM, "컴퓨터-엔트리코딩프로그래밍B")],
        "key" : "06877C6"
    }
}

if __name__ == "__main__":
    # argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="set test mode")
    parser.add_argument("--child", required=True, help="pick one of your children [hani|joy]")
    args = parser.parse_args()

    driver = create_driver()
    context = browser.Context(driver, table[args.child]["url"], default_timeout=10)

    print(f"{args.child} 수강신청. 시작을 원하시면 enter를 누르세요.")
    input()


    ############# 수강신청 준비 ##############
    # TODO: 이 구간의 변경이 일어난다면 수강신청을 제대로 할 수 없다. 따라서
    # 만약의 경우 (ex. 버튼 이름 변경)를 대비하여 강제로 시작할 수 있도록 구현이
    # 필요하다.

    while not is_application_period(context) and not args.test:
        print("수강신청 기간이 아닙니다.")
        time.sleep(0.5)
        context.refresh()


    # 수강신청 버튼이 나타날때 까지 대기 (수강신청 기간이 아닙니다 는 사라지고,
    # 약 70초 이후에 수강신청/확인 버튼이 활성화된다. 
    # 약 1초에 한번씩 refesh 되는 것으로 보이는데 button element가 DOM 에 갑자기
    # 등장한다.
    btn = browser.ClickableElement(context, by="xpath",
                                       path=f"//a[contains(text(), '수강신청/확인')]")
    if not btn.exist(timeout = 120):
        print("Failed to find 수강신청 button")


    ########### 수강 신청 ################
    # XXX: 이구간은 미리 파악 할 수 있기 때문에 큰 변경사항은 없을 것이다.
    for cls in table[args.child]["classes"]:
        cat: Category = cls[0]
        name = cls[1]

        # 수강신청 페이지로 이동
        context.set_url(
            f"https://www.afteredu.kr/register/subscribe1.asp?school_id=120023&subject_do={cat.value}&inning=2023-1&ukey={table[args.child]['key']}")

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
