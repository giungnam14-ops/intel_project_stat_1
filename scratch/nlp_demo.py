import random
from collections import Counter
import re

# 1. 가상 데이터 생성 (Mock Data Generation)
# 각 자치구별로 특징적인 리뷰 텍스트 세트를 가상으로 만듭니다.
MOCK_REVIEWS = {
    "강남구": [
        "분위기는 정말 고급스럽고 좋은데 가격이 너무 비싸요. 주차하기가 힘듭니다.",
        "직장인 회식하기 딱 좋은 곳! 서비스도 훌륭하고 맛도 최고입니다.",
        "트렌디한 카페가 많아서 데이트 코스로 완벽해요. 웨이팅은 필수 ㅠㅠ",
        "비싼 임대료 때문인지 음식 값이 상당하지만 퀄리티는 보장됩니다. 고급 식당 추천.",
        "교통이 편리해서 모임 장소로 자주 이용합니다. 예약 안 하면 자리 없어요."
    ],
    "마포구": [
        "가성비 넘치는 맛집들이 정말 많아요! 힙한 분위기 최고.",
        "젊은 사람들이 많아서 활기찬 분위기. 골목골목 숨은 카페 찾는 재미가 쏠쏠함.",
        "저렴하고 맛있는 술집이 많아서 친구들이랑 자주 갑니다. 시끄러운 건 감수해야 함.",
        "개성 넘치는 소품샵과 빈티지 샵들이 많아 구경하기 좋아요. 핫플 인정!",
        "길거리 공연도 볼 수 있고 에너지가 넘치는 상권입니다. 가성비 갑."
    ],
    "성동구": [
        "옛날 공장을 개조한 감성 카페들이 너무 예뻐요. 사진 찍기 좋은 곳 투성이!",
        "요즘 가장 핫한 동네. 팝업 스토어도 많고 볼거리가 풍부합니다. 주차는 최악.",
        "독특한 컨셉의 식당들이 많아서 좋아요. 가격대는 좀 있는 편.",
        "힙스터들의 성지. 골목마다 특유의 레트로한 분위기가 매력적입니다.",
        "수제 맥주집이 많아서 퇴근 후 한 잔 하기 딱 좋습니다. 감성 충만."
    ]
}

# 간단한 감성 사전 (긍정/부정 단어)
POSITIVE_WORDS = ['좋은', '훌륭하고', '최고', '완벽해요', '보장됩니다', '편리해서', '가성비', '힙한', '맛있는', '좋아요', '인정', '에너지가', '예뻐요', '핫한', '풍부합니다', '독특한', '매력적입니다']
NEGATIVE_WORDS = ['비싸요', '힘듭니다', '웨이팅은', '비싼', '없어요', '시끄러운', '최악']
STOP_WORDS = ['너무', '정말', '딱', '많아서', '많아', '좀', '수', '있는', '곳', '하는']

def clean_text(text):
    """특수문자 제거 및 소문자 변환"""
    text = re.sub(r'[^\w\s]', '', text)
    return text

def analyze_district(district_name):
    print(f"\n[{district_name} 비정형 데이터 분석 결과]")
    reviews = MOCK_REVIEWS.get(district_name, [])
    
    all_words = []
    positive_score = 0
    negative_score = 0
    
    for review in reviews:
        cleaned_review = clean_text(review)
        words = cleaned_review.split()
        
        for word in words:
            if word in STOP_WORDS:
                continue
            
            # 단어 빈도수 집계를 위해 저장 (형태소 분석기 대용으로 임시 처리)
            if len(word) > 1:
                all_words.append(word)
                
            # 감성 분석 스코어 계산
            if any(pos in word for pos in POSITIVE_WORDS):
                positive_score += 1
            elif any(neg in word for neg in NEGATIVE_WORDS):
                negative_score += 1

    # 가장 많이 언급된 키워드 (Word Cloud용)
    word_counts = Counter(all_words)
    top_keywords = word_counts.most_common(5)
    
    # 긍/부정 비율 계산
    total_sentiment = positive_score + negative_score
    if total_sentiment > 0:
        pos_ratio = (positive_score / total_sentiment) * 100
        neg_ratio = (negative_score / total_sentiment) * 100
    else:
        pos_ratio, neg_ratio = 50, 50
        
    print("-" * 40)
    print("[주요 키워드 TOP 5]")
    for word, count in top_keywords:
        print(f"  - {word}: {count}회 언급")
        
    print("\n[감성 분석 (Sentiment)]")
    print(f"  - 긍정 평가: {pos_ratio:.1f}%")
    print(f"  - 부정 평가: {neg_ratio:.1f}%")
    print("-" * 40)

if __name__ == "__main__":
    print("=== 상권 비정형 데이터(리뷰) 분석 프로세스 데모 ===")
    analyze_district("강남구")
    analyze_district("마포구")
    analyze_district("성동구")
