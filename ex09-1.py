import pygame
import random
import sys

# 초기화
pygame.init()

# 배경음악 추가
pygame.mixer.init()
pygame.mixer.music.load("c:/python/02-pygame/speed-music.mp3")  # 파일 경로에 맞게 수정
pygame.mixer.music.play(-1)  # -1은 무한 반복

# 효과음 추가
car_passing_sound = pygame.mixer.Sound("c:/python/02-pygame/car-passing.wav")

# 화면 크기 설정
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 640
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("F1 Racing")

# FPS
clock = pygame.time.Clock()

# 플레이어(캐릭터) 설정
player_width = 50
player_height = 80
player_x = (SCREEN_WIDTH - player_width) // 2
player_y = SCREEN_HEIGHT - player_height - 10
player_speed = 7
player_image = pygame.image.load("c:/python/02-pygame/image/car1.png")
player_image = pygame.transform.scale(player_image, (player_width, player_height))
player_mask = pygame.mask.from_surface(player_image)

# 공 설정
ball_width = 80
ball_height = 100
ball_speed = 5
ball_image = pygame.image.load("c:/python/02-pygame/image/RacingCar/RacingCar_0.png")
ball_image = pygame.transform.scale(ball_image, (ball_width, ball_height))
ball_mask = pygame.mask.from_surface(ball_image)

# car3 이미지 추가 (축소)
car3_width = 60
car3_height = 75
car3_image = pygame.image.load("c:/python/02-pygame/image/car3.png")
car3_image = pygame.transform.scale(car3_image, (car3_width, car3_height))
car3_mask = pygame.mask.from_surface(car3_image)

# 공 리스트 (여러 개의 공을 관리)
balls = []
for i in range(1):  # 초기에는 1개
    ball = {
        'x': random.randint(80, SCREEN_WIDTH - ball_width - 80),
        'y': random.randint(-200, -100),
        'speed': ball_speed,
        'type': random.choices(['racing', 'car3'], weights=[80, 20])[0]  # racing 80%, car3 20%
    }
    balls.append(ball)

# 배경 이미지
background_image = pygame.image.load("c:/python/02-pygame/road.png")
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
background_y = 0
background_speed = 8

# 속도 증가 설정
speed_increase_timer = 0
speed_increase_interval = 1500  # 1초마다 속도 증가
max_ball_speed = 18  # 공 최고 속도
max_background_speed = 20  # 배경 최고 속도

# 점수
score = 0
# 폰트 경로 지정 (한글 지원)
FONT_PATH = "c:/python/02-pygame/malgun.ttf"

# 폰트 크기 일괄 축소 (3/4)
font = pygame.font.Font(FONT_PATH, 27)  # 36*0.75=27
# title_font = pygame.font.Font(FONT_PATH, 36)  # 48*0.75=36
# high_score_font = pygame.font.Font(FONT_PATH, 27)  # 36*0.75=27
# font_input = pygame.font.Font(FONT_PATH, 36)  # 48*0.75=36
# info_font = pygame.font.Font(FONT_PATH, 24)  # 32*0.75=24
# msg_font = pygame.font.Font(FONT_PATH, 27)  # 36*0.75=27

# 최고 기록 관리 (이름, 점수 쌍)
def load_high_scores():
    try:
        with open('c:/python/02-pygame/high_scores.txt', 'r', encoding='utf-8') as f:
            scores = []
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    name, score = parts
                    scores.append((name, int(score)))
            while len(scores) < 3:
                scores.append(("---", 0))
            return scores[:3]
    except FileNotFoundError:
        return [("---", 0), ("---", 0), ("---", 0)]

def save_high_scores(scores):
    with open('c:/python/02-pygame/high_scores.txt', 'w', encoding='utf-8') as f:
        for name, score in scores:
            f.write(f"{name},{score}\n")

def update_high_scores(current_score, current_name):
    scores = load_high_scores()
    scores.append((current_name, current_score))
    scores.sort(key=lambda x: x[1], reverse=True)  # 점수 기준 내림차순
    return scores[:3]

# 이름 입력 함수 (Pygame 텍스트 입력)
def get_player_name():
    input_box = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = True
    text = ''
    # font_input = pygame.font.Font(FONT_PATH, 36)
    # info_font = pygame.font.Font(FONT_PATH, 24)
    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if text.strip() != '':
                        return text[:6]
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    if len(text) < 6:
                        if event.unicode.isprintable() and (event.unicode.isalnum() or '\uac00' <= event.unicode <= '\ud7a3'):
                            text += event.unicode
        screen.fill((255, 255, 255))
        prompt = font.render("Enter your name (최대 6자):", True, (0, 0, 0)) # info_font.render
        screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT//2 - 60))
        txt_surface = font.render(text, True, color) # font_input.render
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(screen, color, input_box, 2)
        pygame.display.flip()
        clock.tick(30)
    return text[:6] if text else "---"

def draw_player(x, y):
    screen.blit(player_image, (x, y))

def draw_ball(ball):
    if ball['type'] == 'racing':
        screen.blit(ball_image, (ball['x'], ball['y']))
    else:  # car3
        screen.blit(car3_image, (ball['x'], ball['y']))

def show_score(score):
    text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

def main():
    global player_x, score, background_y, ball_speed, background_speed, speed_increase_timer, balls
    # 속도 회복 관련 변수
    speed_recovering = False
    recover_timer = 0
    recover_interval = 1000  # 1초마다 회복
    target_ball_speed = ball_speed
    target_background_speed = background_speed

    # --- 데모 모드(5초) ---
    demo_duration = 5000  # 5초 (ms)
    demo_start_time = pygame.time.get_ticks()
    demo_player_x = player_x
    demo_direction = 1  # 1: 오른쪽, -1: 왼쪽
    demo_background_y = background_y
    r_key_count = 0
    r_key_last_time = 0
    reset_message_time = 0
    reset_message_show = False
    while pygame.time.get_ticks() - demo_start_time < demo_duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    now = pygame.time.get_ticks()
                    # 1초 이내 연속 입력만 인정
                    if now - r_key_last_time < 1000:
                        r_key_count += 1
                    else:
                        r_key_count = 1
                    r_key_last_time = now
                    if r_key_count == 3:
                        # Top3 기록 리셋
                        save_high_scores([("---", 0), ("---", 0), ("---", 0)])
                        reset_message_time = now
                        reset_message_show = True
                        r_key_count = 0
        # player 자동 좌우 이동
        demo_player_x += demo_direction * 4
        if demo_player_x > SCREEN_WIDTH - player_width - 80:
            demo_direction = -1
        if demo_player_x < 80:
            demo_direction = 1
        # 공 자동 이동
        for ball in balls:
            ball['y'] += ball['speed']
            if ball['y'] > SCREEN_HEIGHT:
                ball['y'] = random.randint(-200, -100)
                ball['x'] = random.randint(80, SCREEN_WIDTH - ball_width - 80)
        # 배경 이동
        demo_background_y = (demo_background_y + background_speed) % SCREEN_HEIGHT
        # 화면 그리기
        screen.blit(background_image, (0, demo_background_y))
        screen.blit(background_image, (0, demo_background_y - SCREEN_HEIGHT))
        draw_player(demo_player_x, player_y)
        for ball in balls:
            draw_ball(ball)
        # Top3 점수 표시
        high_scores = load_high_scores()
        # high_score_font = pygame.font.Font(FONT_PATH, 28) # 21
        high_score_text1 = font.render(f"1st: {high_scores[0][0]} {high_scores[0][1]}", True, (255, 215, 0)) # 21
        high_score_text2 = font.render(f"2nd: {high_scores[1][0]} {high_scores[1][1]}", True, (192, 192, 192)) # 21
        high_score_text3 = font.render(f"3rd: {high_scores[2][0]} {high_scores[2][1]}", True, (205, 127, 50)) # 21
        screen.blit(high_score_text1, (10, 50))
        screen.blit(high_score_text2, (10, 80))
        screen.blit(high_score_text3, (10, 110))
        # demo_text = high_score_font.render("Demo Mode", True, (0, 255, 255)) # 21
        demo_text = font.render("Demo Mode", True, (0, 255, 255)) # 21
        screen.blit(demo_text, (SCREEN_WIDTH//2 - demo_text.get_width()//2, 20))
        
        # 방향키 안내 텍스트 추가
        controls_text = font.render("Left ← → Right", True, (255, 255, 255))
        screen.blit(controls_text, (SCREEN_WIDTH//2 - controls_text.get_width()//2, SCREEN_HEIGHT - 40))
        
        if reset_message_show:
            # msg_font = pygame.font.Font(FONT_PATH, 36) # 27
            msg = font.render("Top3 기록이 리셋되었습니다!", True, (255, 0, 0)) # 27
            screen.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, SCREEN_HEIGHT//2 - 100))
            if pygame.time.get_ticks() - reset_message_time > 1000:
                reset_message_show = False
        pygame.display.flip()
        clock.tick(60)

    # 데모 후 player, ball, 배경 위치 초기화
    player_x = (SCREEN_WIDTH - player_width) // 2
    background_y = 0
    balls.clear()
    for i in range(1):
        ball = {
            'x': random.randint(80, SCREEN_WIDTH - ball_width - 80),
            'y': random.randint(-200, -100),
            'speed': ball_speed,
            'type': random.choices(['racing', 'car3'], weights=[80, 20])[0]
        }
        balls.append(ball)

    # Top3 점수 표시 (게임 시작 전)
    high_scores = load_high_scores()
    screen.fill((0, 0, 0))
    # title_font = pygame.font.Font(FONT_PATH, 48) # 36
    title_text = font.render("Top 3 Scores", True, (255, 255, 0)) # 36
    screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, 100))
    # high_score_font = pygame.font.Font(FONT_PATH, 36) # 27
    high_score_text1 = font.render(f"1st: {high_scores[0][0]} {high_scores[0][1]}", True, (255, 215, 0)) # 27
    high_score_text2 = font.render(f"2nd: {high_scores[1][0]} {high_scores[1][1]}", True, (192, 192, 192)) # 27
    high_score_text3 = font.render(f"3rd: {high_scores[2][0]} {high_scores[2][1]}", True, (205, 127, 50)) # 27
    screen.blit(high_score_text1, (SCREEN_WIDTH//2 - high_score_text1.get_width()//2, 180))
    screen.blit(high_score_text2, (SCREEN_WIDTH//2 - high_score_text2.get_width()//2, 220))
    screen.blit(high_score_text3, (SCREEN_WIDTH//2 - high_score_text3.get_width()//2, 260))
    pygame.display.flip()
    pygame.time.delay(2000)  # 2초간 표시
    # 카운트다운 애니메이션
    countdown_list = ["3", "2", "1", "START!"]
    for count_str in countdown_list:
        for size in range(45, 151, 10):  # 60~200까지 14씩 증가 (애니메이션 단계)
            screen.fill((0, 0, 0))
            # countdown_font = pygame.font.Font(FONT_PATH, size)
            countdown_font = pygame.font.Font(FONT_PATH, size)
            text = countdown_font.render(count_str, True, (255, 255, 255))
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(text, text_rect)
            pygame.display.flip()
            pygame.time.delay(50)
        pygame.time.delay(300)  # 마지막 크기에서 잠깐 멈춤
    # 본 게임 루프 시작
    running = True
    while running:
        clock.tick(60)
        dt = clock.get_time()  # ms
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # 키 입력 처리
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= player_speed
        if keys[pygame.K_RIGHT]:
            player_x += player_speed
        if keys[pygame.K_UP]:
            ball_speed = min(ball_speed + 0.5, max_ball_speed)
            background_speed = min(background_speed + 0.5, max_background_speed)
        if keys[pygame.K_DOWN]:
            ball_speed = max(ball_speed - 0.5, 1)
            background_speed = max(background_speed - 0.5, 1)

        # 플레이어가 화면 밖으로 나가지 않게 (좌우 80픽셀 제한)
        player_x = max(80, min(SCREEN_WIDTH - player_width - 80, player_x))

        # 배경 이동 (Top Down 효과)
        background_y += background_speed
        if background_y >= SCREEN_HEIGHT:
            background_y = 0

        # 속도 증가 및 공 개수 조절
        speed_increase_timer += clock.get_time()
        if speed_increase_timer >= speed_increase_interval:
            ball_speed = min(ball_speed + 0.4, max_ball_speed)
            background_speed = min(background_speed + 0.5, max_background_speed)
            speed_increase_timer = 0
            
            # 점수에 따라 공 개수 증가 (10점마다 공 1개씩 추가, 최대 3개)
            if score > 0 and score % 10 == 0 and len(balls) < 3:
                # 새로운 공이 기존 공과 겹치지 않도록 위치 조정
                attempts = 0
                while attempts < 50:  # 최대 50번 시도
                    new_x = random.randint(80, SCREEN_WIDTH - ball_width - 80)
                    new_y = random.randint(-200, -100)
                    
                    # 기존 공들과의 거리 체크
                    too_close = False
                    for ball in balls:
                        distance = ((new_x - ball['x'])**2 + (new_y - ball['y'])**2)**0.5
                        if distance < ball_width + 20:  # 최소 20픽셀 간격
                            too_close = True
                            break
                    
                    if not too_close:
                        new_ball = {
                            'x': new_x,
                            'y': new_y,
                            'speed': ball_speed,
                            'type': random.choices(['racing', 'car3'], weights=[80, 20])[0]
                        }
                        balls.append(new_ball)
                        break
                    
                    attempts += 1
                
                # 50번 시도해도 안되면 강제로 추가 (최소한의 간격으로)
                if attempts >= 50:
                    new_ball = {
                        'x': random.randint(80, SCREEN_WIDTH - ball_width - 80),
                        'y': random.randint(-200, -100),
                        'speed': ball_speed,
                        'type': random.choices(['racing', 'car3'], weights=[80, 20])[0]
                    }
                    balls.append(new_ball)

        # 공 이동
        for ball in balls:
            ball['y'] += ball['speed']
            if ball['y'] > SCREEN_HEIGHT:
                # 공이 화면 아래로 나가면 새로운 위치로 재배치 (겹치지 않도록)
                attempts = 0
                while attempts < 50:
                    new_x = random.randint(80, SCREEN_WIDTH - ball_width - 80)
                    new_y = random.randint(-200, -100)
                    
                    # 다른 공들과의 거리 체크
                    too_close = False
                    for other_ball in balls:
                        if other_ball != ball:  # 자기 자신 제외
                            distance = ((new_x - other_ball['x'])**2 + (new_y - other_ball['y'])**2)**0.5
                            if distance < ball_width + 20:
                                too_close = True
                                break
                    
                    if not too_close:
                        ball['x'] = new_x
                        ball['y'] = new_y
                        ball['speed'] = ball_speed
                        score += 1
                        if score % 5 == 0:
                            car_passing_sound.play()  # 5점 단위로만 효과음 재생
                        # 스코어 100 달성 시 게임 종료
                        if score >= 100:
                            running = False
                        break
                    
                    attempts += 1
                
                # 50번 시도해도 안되면 강제로 재배치
                if attempts >= 50:
                    ball['y'] = random.randint(-200, -100)
                    ball['x'] = random.randint(80, SCREEN_WIDTH - ball_width - 80)
                    ball['speed'] = ball_speed
                    score += 1
                    if score % 5 == 0:
                        car_passing_sound.play()  # 5점 단위로만 효과음 재생
                    # 스코어 100 달성 시 게임 종료
                    if score >= 100:
                        running = False

        # 속도 회복 처리
        if speed_recovering:
            recover_timer += dt
            if recover_timer >= recover_interval:
                recover_timer = 0
                if ball_speed < target_ball_speed:
                    ball_speed = min(ball_speed + 1, target_ball_speed)
                if background_speed < target_background_speed:
                    background_speed = min(background_speed + 1, target_background_speed)
                # 모두 회복되면 중지
                if ball_speed >= target_ball_speed and background_speed >= target_background_speed:
                    speed_recovering = False

        # 충돌 체크
        for ball in balls:
            offset = (int(ball['x'] - player_x), int(ball['y'] - player_y))
            if ball['type'] == 'racing':
                if player_mask.overlap(ball_mask, offset):
                    running = False
                    break
            else:  # car3
                if player_mask.overlap(car3_mask, offset):
                    # car3과 충돌 시 속도 감소
                    ball_speed = max(ball_speed - 2, 1)  # 최소 속도 1 유지
                    background_speed = max(background_speed - 2, 1)  # 최소 속도 1 유지
                    # 회복 타겟은 현재 점수 기반 최대값
                    target_ball_speed = min(5 + (score // 10) * 0.4, 18)  # ball_speed 증가 로직과 동일
                    target_background_speed = min(8 + (score // 10) * 0.5, 20)  # background_speed 증가 로직과 동일
                    speed_recovering = True
                    recover_timer = 0
                    # 충돌한 car3 제거
                    balls.remove(ball)
                    # 새로운 공으로 대체 (갯수 유지)
                    new_ball = {
                        'x': random.randint(80, SCREEN_WIDTH - ball_width - 80),
                        'y': random.randint(-200, -100),
                        'speed': ball_speed,
                        'type': random.choices(['racing', 'car3'], weights=[80, 20])[0]
                    }
                    balls.append(new_ball)
                    break
        # 화면 그리기
        # 배경을 두 번 그려서 무한 스크롤 효과 생성
        screen.blit(background_image, (0, background_y))
        screen.blit(background_image, (0, background_y - SCREEN_HEIGHT))
        draw_player(player_x, player_y)
        for ball in balls:
            draw_ball(ball)
        show_score(score)
        pygame.display.flip()

    # 최고 기록 업데이트 (이름 입력 포함)
    high_scores = load_high_scores()
    # Top3 진입 여부 확인
    if score > 0 and (score > high_scores[2][1]):
        # 이름 입력
        player_name = get_player_name()
        high_scores = update_high_scores(score, player_name)
        save_high_scores(high_scores)
    else:
        high_scores = update_high_scores(score, "---")
        save_high_scores(high_scores)
    
    # 게임 종료 화면 (Goal 또는 Game Over)
    waiting_for_input = True
    end_screen_start_time = pygame.time.get_ticks()  # 종료 화면 진입 시간 저장
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.mixer.music.stop()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # ESC로 종료
                    pygame.mixer.music.stop()
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_SPACE:  # 스페이스로 재시작
                    waiting_for_input = False
                    # 게임 상태 초기화
                    player_x = (SCREEN_WIDTH - player_width) // 2
                    ball_speed = 5
                    background_speed = 8
                    speed_increase_timer = 0
                    balls = []
                    for i in range(1):
                        ball = {
                            'x': random.randint(80, SCREEN_WIDTH - ball_width - 80),
                            'y': random.randint(-200, -100),
                            'speed': ball_speed,
                            'type': random.choices(['racing', 'car3'], weights=[80, 20])[0]
                        }
                        balls.append(ball)
                    score = 0
                    main()  # 게임 재시작
                    return
        # 5초가 지나면 자동으로 데모 모드로 이동
        if pygame.time.get_ticks() - end_screen_start_time > 5000:
            waiting_for_input = False
            break
        # 게임 종료 화면 그리기
        screen.fill((0, 0, 0))
        
        # 폰트 크기 조정
        gameover_font = pygame.font.Font(FONT_PATH, int(27 * 1.5))  # 기존 font 크기의 1.5배
        
        # 스코어 100 달성 시 Goal, 아니면 Game Over
        if score >= 100:
            game_over_text = gameover_font.render("GOAL!", True, (0, 255, 0))  # 초록색
        else:
            game_over_text = gameover_font.render("Game Over!", True, (255, 0, 0))  # 빨간색
        
        score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
        
        # 최고 기록 표시 (이름+점수)
        high_scores = load_high_scores()
        high_score_text1 = font.render(f"1st: {high_scores[0][0]} {high_scores[0][1]}", True, (255, 215, 0))  # 금색
        high_score_text2 = font.render(f"2nd: {high_scores[1][0]} {high_scores[1][1]}", True, (192, 192, 192))  # 은색
        high_score_text3 = font.render(f"3rd: {high_scores[2][0]} {high_scores[2][1]}", True, (205, 127, 50))  # 동색
        
        restart_text1 = font.render("Press SPACE to Restart", True, (255, 255, 255))
        restart_text2 = font.render("Press ESC to Quit", True, (255, 255, 255))
        
        # 줄 간격 계산 (폰트 크기 기준)
        line_gap = 20
        y = SCREEN_HEIGHT//2 - 120
        # Game Over/Goal
        screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, y))
        y += game_over_text.get_height() + line_gap
        # Final Score
        screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, y))
        y += score_text.get_height() + line_gap
        # Top3
        screen.blit(high_score_text1, (SCREEN_WIDTH//2 - high_score_text1.get_width()//2, y))
        y += high_score_text1.get_height()
        screen.blit(high_score_text2, (SCREEN_WIDTH//2 - high_score_text2.get_width()//2, y))
        y += high_score_text2.get_height()
        screen.blit(high_score_text3, (SCREEN_WIDTH//2 - high_score_text3.get_width()//2, y))
        y += high_score_text3.get_height() + line_gap
        # Restart 안내
        screen.blit(restart_text1, (SCREEN_WIDTH//2 - restart_text1.get_width()//2, y))
        y += restart_text1.get_height()
        screen.blit(restart_text2, (SCREEN_WIDTH//2 - restart_text2.get_width()//2, y))
        
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
