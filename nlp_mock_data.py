import random
from collections import Counter
import re

# 서울시 25개 자치구별 가상 비정형 데이터 (리뷰/SNS 반응)
MOCK_REVIEWS = {
    "강남구": [
        "분위기는 고급스러운데 가격이 너무 비싸요. 주차 헬입니다.",
        "직장인 회식 성지! 서비스 훌륭하고 맛 최고입니다.",
        "트렌디한 카페가 많아서 데이트하기 좋아요. 웨이팅은 필수 ㅠㅠ",
        "비싼 임대료 때문인지 비싸지만 퀄리티 보장됩니다. 고급 식당 추천.",
        "교통 편리해서 모임 장소로 딱입니다. 예약 필수."
    ],
    "마포구": [
        "가성비 넘치는 맛집 많아요! 힙한 분위기 최고.",
        "젊은 사람들이 많아서 활기찬 분위기. 숨은 카페 찾는 재미가 쏠쏠함.",
        "저렴하고 맛있는 술집 많아서 친구들이랑 자주 갑니다.",
        "개성 넘치는 소품샵과 빈티지 샵이 많아 구경하기 좋아요. 핫플 인정!",
        "길거리 공연도 볼 수 있고 에너지 넘치는 상권입니다. 가성비 갑."
    ],
    "성동구": [
        "옛날 공장을 개조한 감성 카페들이 너무 예뻐요. 사진 맛집!",
        "요즘 핫한 성수동. 팝업 스토어 많고 볼거리 풍부합니다. 주차는 최악.",
        "독특한 컨셉 식당들이 많아서 좋아요. 가격대는 좀 있는 편.",
        "힙스터들의 성지. 골목마다 특유의 레트로한 분위기가 매력적입니다.",
        "수제 맥주집 많아서 퇴근 후 한 잔 하기 딱 좋습니다. 감성 충만."
    ],
    "종로구": [
        "노포 감성 미쳤습니다. 낡았지만 맛은 확실한 곳들.",
        "직장인 아재 입맛 저격하는 맛집이 널렸어요. 가성비 나쁘지 않음.",
        "길거리가 좁고 복잡하지만 특유의 분위기가 너무 좋아요.",
        "오래된 전통 맛집이 많아 실패할 확률이 적습니다.",
        "퇴근길에 삼겹살에 소주 한잔 하기 최고의 상권."
    ],
    "서초구": [
        "조용하고 고급스러운 다이닝이 많아서 모임하기 좋습니다.",
        "가격대가 좀 높지만 분위기 내기에는 최고의 동네입니다.",
        "주차가 편리한 식당이 많아서 차 타고 가기 좋아요.",
        "브런치 카페나 디저트 맛집이 골목마다 숨어있습니다.",
        "법원 근처라 그런지 직장인 대상 깔끔한 밥집이 많습니다."
    ],
    "영등포구": [
        "대형 쇼핑몰 근처라 유동인구 엄청나고 복잡해요.",
        "노포와 프랜차이즈가 섞여 있어서 선택지가 많습니다.",
        "여의도 직장인들 점심시간 웨이팅 장난 아닙니다. 물가 비쌈.",
        "가성비 좋은 고기집이 많아서 회식하기 아주 좋아요.",
        "오래된 상권이라 낡은 느낌도 있지만 맛집은 확실함."
    ],
    # 다른 자치구들의 기본 데이터
    "DEFAULT": [
        "동네 주민들이 주로 가는 로컬 맛집이 많습니다.",
        "무난하게 식사하기 좋은 식당들이 모여있어요.",
        "특별히 핫플은 없지만 조용하고 가성비 좋습니다.",
        "최근 새로운 카페들이 하나둘 생기고 있는 추세입니다.",
        "가족 단위로 외식하기 좋은 깔끔한 식당이 좀 필요해요."
    ]
}

POSITIVE_WORDS = ['좋은', '훌륭하고', '최고', '완벽해요', '보장됩니다', '편리해서', '가성비', '힙한', '맛있는', '좋아요', '인정', '에너지', '예뻐요', '핫한', '풍부합니다', '독특한', '매력적', '감성', '확실한', '편리한', '깔끔한']
NEGATIVE_WORDS = ['비싸요', '힘듭니다', '웨이팅', '비싼', '없어요', '시끄러운', '최악', '낡은', '복잡해요', '헬', '비쌈']
STOP_WORDS = ['너무', '정말', '딱', '많아서', '많아', '좀', '수', '있는', '곳', '하는', '많아요', '많습니다', '입니다', '있는', '가장', '근처라']

def get_unstructured_data(district_name):
    reviews = MOCK_REVIEWS.get(district_name, MOCK_REVIEWS["DEFAULT"])
    
    all_words = []
    positive_score = 0
    negative_score = 0
    
    for review in reviews:
        # 단어 추출 (특수문자 제거 후 공백 분리)
        clean_review = re.sub(r'[^\w\s]', '', review)
        words = clean_review.split()
        
        for word in words:
            if word in STOP_WORDS or len(word) < 2:
                continue
            all_words.append(word)
            
            if any(pos in word for pos in POSITIVE_WORDS):
                positive_score += 1
            elif any(neg in word for neg in NEGATIVE_WORDS):
                negative_score += 1

    word_counts = Counter(all_words)
    top_keywords = [{"word": word, "count": count} for word, count in word_counts.most_common(6)]
    
    total_sentiment = positive_score + negative_score
    if total_sentiment > 0:
        pos_ratio = round((positive_score / total_sentiment) * 100, 1)
        neg_ratio = round((negative_score / total_sentiment) * 100, 1)
    else:
        pos_ratio, neg_ratio = 50.0, 50.0
        
    return {
        "reviews": reviews[:3], # 화면에 보여줄 리뷰 3개
        "keywords": top_keywords,
        "sentiment": {
            "positive": pos_ratio,
            "negative": neg_ratio
        }
    }
