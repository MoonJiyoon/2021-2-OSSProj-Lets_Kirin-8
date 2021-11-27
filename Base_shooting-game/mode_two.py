import pygame
import random
from collections import deque
import sys

from sprites import (MasterSprite, Ship2, Ship3, Friendship, Alien, Missile, BombPowerup,
                     ShieldPowerup, DoublemissilePowerup, FriendPowerup, Explosion, Siney, Spikey, Fasty,
                     Roundy, Crawly)
from database import Database
from load import load_image, load_sound, load_music

if not pygame.mixer:
    print('Warning, sound disabled')
if not pygame.font:
    print('Warning, fonts disabled')

BLUE = (0, 0, 255)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

direction = {None: (0, 0), pygame.K_UP: (0, -2), pygame.K_DOWN: (0, 2),
             pygame.K_LEFT: (-2, 0), pygame.K_RIGHT: (2, 0)}

direction2 = {None: (0, 0), pygame.K_w: (0, -2), pygame.K_s: (0, 2),
             pygame.K_a: (-2, 0), pygame.K_d: (2, 0)}


class Keyboard(object):
    keys = {pygame.K_a: 'A', pygame.K_b: 'B', pygame.K_c: 'C', pygame.K_d: 'D',
            pygame.K_e: 'E', pygame.K_f: 'F', pygame.K_g: 'G', pygame.K_h: 'H',
            pygame.K_i: 'I', pygame.K_j: 'J', pygame.K_k: 'K', pygame.K_l: 'L',
            pygame.K_m: 'M', pygame.K_n: 'N', pygame.K_o: 'O', pygame.K_p: 'P',
            pygame.K_q: 'Q', pygame.K_r: 'R', pygame.K_s: 'S', pygame.K_t: 'T',
            pygame.K_u: 'U', pygame.K_v: 'V', pygame.K_w: 'W', pygame.K_x: 'X',
            pygame.K_y: 'Y', pygame.K_z: 'Z'}


def main(): 
    # Initialize everything
    pygame.mixer.pre_init(11025, -16, 2, 512)
    pygame.init()
    screen = pygame.display.set_mode((500, 500))
    pygame.display.set_caption('Shooting Game')
    pygame.mouse.set_visible(0)

    def kill_alien(alien, aliensLeftThisWave, score) :
        aliensLeftThisWave -= 1
        if alien.pType == 'green':
            score += 1
        elif alien.pType == 'orange':
            score += 2
        elif alien.pType == 'red':
            score += 4
        elif alien.pType == 'yellow':
            score += 8
        return aliensLeftThisWave, score
    
    def background_update(screen, background, backgroundLoc) :
        screen.blit(
            background, (0, 0), area=pygame.Rect(
                0, backgroundLoc, 500, 500))
        backgroundLoc -= speed
        if backgroundLoc - speed <= speed:
            backgroundLoc = 1500
        return screen, background, backgroundLoc

    # 인게임에서 배경색으로 플레이어 영역 구분
    def background_update_half(screen, background, backgroundLoc) :
        screen.blit(
            background, (0, 0), area=pygame.Rect(
                0, backgroundLoc, 500, 500))
        screen.fill((80, 20, 30, 125),(0, 0, screen.get_width()//2, screen.get_height()), special_flags = 1) # special_flags = 3 : 별 색깔만 바뀜
        backgroundLoc -= speed
        if backgroundLoc - speed <= speed:
            backgroundLoc = 1500
        return screen, background, backgroundLoc

    def background_update_half_two(screen, background, backgroundLoc) :
        screen.blit(
            background, (0, 0), area=pygame.Rect(
                0, backgroundLoc, 500, 500))
        screen.fill((80, 20, 30, 125),(screen.get_width()//2, 0, screen.get_width()//size.x_background_ratio, screen.get_height()), special_flags = 1)
        backgroundLoc -= speed
        if backgroundLoc - speed <= speed:
            backgroundLoc = 1500
        return screen, background, backgroundLoc

    # def ingame_text_update() :
    #     return [font.render("Wave: " + str(wave), 1, WHITE),
    #             font.render("Aliens Left: " + str(aliensLeftThisWave), 1, WHITE),
    #             font.render("Score: " + str(score), 1, WHITE),
    #             font.render("Score: " + str(score2), 1, WHITE),
    #             font.render("Bombs: " + str(bombsHeld), 1, WHITE),
    #             font.render("Bombs: " + str(bombsHeld2), 1, WHITE),
    #             # font.render("Life: ", 1, WHITE)
    #             # font.render("Life: ", 1, WHITE)
    #             font.render('PLAYER 1 WIN!', 1, WHITE),
    #             font.render('PLAYER 2 WIN!', 1, WHITE),
    #             font.render('DRAW!', 1, WHITE)]

# Create the background which will scroll and loop over a set of different
# size stars
    background = pygame.Surface((500, 2000))
    background = background.convert()
    background.fill((0, 0, 0))
    backgroundLoc = 1500
    finalStars = deque()
    for y in range(0, 1500, 30):
        size = random.randint(2, 5)
        x = random.randint(0, 500 - size)
        if y <= 500:
            finalStars.appendleft((x, y + 1500, size))
        pygame.draw.rect(
            background, (255, 255, 0), pygame.Rect(x, y, size, size))
    while finalStars:
        x, y, size = finalStars.pop()
        pygame.draw.rect(
            background, (255, 255, 0), pygame.Rect(x, y, size, size))

# Display the background
    screen.blit(background, (0, 0))
    pygame.display.flip()

# Prepare game objects
    speed = 1.5
    MasterSprite.speed = speed
    alienPeriod = 60 / speed
    clockTime = 60  # maximum FPS
    clock = pygame.time.Clock()
    ship = Ship2()
    ship2 = Ship3()
    
    
    initialAlienTypes = (Siney, Spikey)
    # 수정
    powerupTypes = (BombPowerup, ShieldPowerup, DoublemissilePowerup, FriendPowerup)

    # pause
    pause,pauseRect = load_image('pause.png')
    pauseRect.midtop = screen.get_rect().inflate(0, -200).midtop
    pauseMenu = False

    # Sprite groups
    alldrawings = pygame.sprite.Group()
    # 수정
    allsprites = pygame.sprite.RenderPlain((ship,ship2))
    MasterSprite.allsprites = allsprites
    Alien.pool = pygame.sprite.Group(
        [alien() for alien in initialAlienTypes for _ in range(5)])
    Alien.active = pygame.sprite.Group()
    Missile.pool = pygame.sprite.Group([Missile() for _ in range(10)]) 
    Missile.active = pygame.sprite.Group()
    Explosion.pool = pygame.sprite.Group([Explosion() for _ in range(10)])
    Explosion.active = pygame.sprite.Group()
    
    # doublemissile = pygame.sprite.Group()
    bombs = pygame.sprite.Group()
    bombs2 = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    # life
    life1, life1Rect = load_image('life.png')
    life2, life2Rect = load_image('life.png')
    life3, life3Rect = load_image('life.png')

    # Sounds
    missile_sound = load_sound('missile.ogg')
    bomb_sound = load_sound('bomb.ogg')
    alien_explode_sound = load_sound('alien_explode.ogg')
    ship_explode_sound = load_sound('ship_explode.ogg')
    load_music('music_loop.ogg')

    alienPeriod = clockTime // 2
    curTime = 0
    aliensThisWave, aliensLeftThisWave, Alien.numOffScreen = 10, 10, 10
    wave = 1
    # 내려오는 미사일 먹으면 8초동안 spacebar로 사용 가능
    doublemissile = False
    doublemissile2 = False
    bombsHeld = 3
    bombsHeld2 = 3
    score = 0
    score2 = 0
    missilesFired = 0
    powerupTime = 10 * clockTime
    powerupTimeLeft = powerupTime
    betweenWaveTime = 3 * clockTime
    betweenWaveCount = betweenWaveTime
    betweenDoubleTime = 8 * clockTime
    betweenDoubleCount = betweenDoubleTime
    betweenDoubleCount2 = betweenDoubleTime
    font = pygame.font.Font(None, 36)
    inMenu = True
    half_tf = True

    # 데베 함수 메뉴 구현
    hiScores=Database().getScores()
    highScoreTexts = [font.render("NAME", 1, RED), #폰트 렌터
                      font.render("SCORE", 1, RED),
                      font.render("ACCURACY", 1, RED)]
    highScorePos = [highScoreTexts[0].get_rect(
                      topleft=screen.get_rect().inflate(-100, -100).topleft),
                    highScoreTexts[1].get_rect(
                      midtop=screen.get_rect().inflate(-100, -100).midtop),
                    highScoreTexts[2].get_rect(
                      topright=screen.get_rect().inflate(-100, -100).topright)]
    for hs in hiScores:
        highScoreTexts.extend([font.render(str(hs[x]), 1, BLUE)
                               for x in range(3)])
        highScorePos.extend([highScoreTexts[x].get_rect(
            topleft=highScorePos[x].bottomleft) for x in range(-3, 0)])

   
    title, titleRect = load_image('title.png')
    titleRect.midtop = screen.get_rect().inflate(0, -200).midtop

    # Main menu 게임 메인 메뉴
    # 폰트 렌더 함수 font.render('글씨',1(옵션인가봄),색깔)
    # 폰트 위치 함수 font객체.get_rect(위치선언변수=기준이미지객체.inflate(좌,표).찐위치)    
    startText = font.render('SELECT MODES', 1, BLUE)
    startPos = startText.get_rect(midtop=titleRect.inflate(0, 100).midbottom)
    hiScoreText = font.render('HIGH SCORES', 1, BLUE)
    hiScorePos = hiScoreText.get_rect(topleft=startPos.bottomleft)
    restartText = font.render('RESTART', 1, BLUE)  # restart 메뉴
    restartPos = restartText.get_rect(bottomleft=hiScorePos.topleft)
    fxText = font.render('SOUND FX ', 1, BLUE)
    fxPos = fxText.get_rect(topleft=hiScorePos.bottomleft)
    fxOnText = font.render('ON', 1, RED)
    fxOffText = font.render('OFF', 1, RED)
    fxOnPos = fxOnText.get_rect(topleft=fxPos.topright)
    fxOffPos = fxOffText.get_rect(topleft=fxPos.topright)
    musicText = font.render('MUSIC', 1, BLUE)
    musicPos = fxText.get_rect(topleft=fxPos.bottomleft)
    musicOnText = font.render('ON', 1, RED)
    musicOffText = font.render('OFF', 1, RED)
    musicOnPos = musicOnText.get_rect(topleft=musicPos.topright)
    musicOffPos = musicOffText.get_rect(topleft=musicPos.topright)
    helpText=font.render('HELP',1,BLUE)
    helpPos=helpText.get_rect(topleft=musicPos.bottomleft)
    quitText = font.render('QUIT', 1, BLUE)
    quitPos = quitText.get_rect(topleft=helpPos.bottomleft)
    selectText = font.render('*', 1, BLUE)
    selectPos = selectText.get_rect(topright=startPos.topleft)

    # Select Mode 안 글씨
    singleText = font.render('SINGLE MODE', 1, BLUE)
    singlePos = singleText.get_rect(midtop=titleRect.inflate(0, 100).midbottom)
    timeText = font.render('TIME MODE', 1, BLUE)
    timePos = timeText.get_rect(topleft=singlePos.bottomleft)
    pvpText = font.render('PVP MODE ', 1, BLUE)
    pvpPos = pvpText.get_rect(topleft=timePos.bottomleft)
    backText=font.render('BACK',1,BLUE)
    backPos=backText.get_rect(topleft=pvpPos.bottomleft)
    selectText = font.render('*', 1, BLUE)
    selectPos = selectText.get_rect(topright=singlePos.topleft)

    menuDict = {1: startPos, 2: hiScorePos, 3:fxPos, 4: musicPos, 5:helpPos,6: quitPos}
    selection = 1
    showSelectModes=False
    showHiScores = False
    soundFX = Database().getSound()
    music = Database().getSound(music=True)

    if music and pygame.mixer: 
        pygame.mixer.music.play(loops=-1)


#########################
#    Start Menu Loop    #
#########################
    while inMenu:
        clock.tick(clockTime) 

        screen, background, backgroundLoc = background_update(screen, background, backgroundLoc)

        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                return
            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_RETURN):
                if showHiScores:
                    showHiScores = False
                elif showSelectModes:
                    showSelectModes = False
                elif selection == 1:
                    showSelectModes=True 
                    inMenu = False
                    inSelectMenu=True
                elif selection == 2:
                    showHiScores = True
                elif selection == 3:
                    soundFX = not soundFX
                    if soundFX:
                        missile_sound.play()
                    Database.setSound(int(soundFX))
                elif selection == 4 and pygame.mixer:
                    music = not music
                    if music:
                        pygame.mixer.music.play(loops=-1)
                    else:
                        pygame.mixer.music.stop()
                    Database.setSound(int(music), music=True)
                elif selection == 5:
                    return 
                elif selection == 6:
                    return
            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_w
                  and selection > 1
                  and not showHiScores
                  and not showSelectModes):
                selection -= 1
            elif (event.type == pygame.KEYDOWN
                  and event.key == pygame.K_s
                  and selection < len(menuDict)
                  and not showHiScores
                  and not showSelectModes):
                selection += 1

        selectPos = selectText.get_rect(topright=menuDict[selection].topleft)

        if showHiScores:
            textOverlays = zip(highScoreTexts, highScorePos)
        elif showSelectModes:
            textOverlays = zip([singleText,timeText,pvpText],[singlePos,timePos,pvpPos])
        else:
            textOverlays = zip([startText, hiScoreText, helpText, fxText,
                                musicText, quitText, selectText,
                                fxOnText if soundFX else fxOffText,
                                musicOnText if music else musicOffText],
                               [startPos, hiScorePos, helpPos, fxPos,
                                musicPos, quitPos, selectPos,
                                fxOnPos if soundFX else fxOffPos,
                                musicOnPos if music else musicOffPos])
            screen.blit(title, titleRect)
        for txt, pos in textOverlays:
            screen.blit(txt, pos)
        pygame.display.flip()

    showSingleMode=False
    showTimeMode=False
    showPvpMode=False
    selectModeDict={1:singlePos,2:timePos,3:pvpPos,4:backPos}
    selection = 1

    while inSelectMenu:
                clock.tick(clockTime) #시간으로 제어하는 너낌
        #blit()
                screen.blit(
                    background, (0, 0), area=pygame.Rect(
                        0, backgroundLoc, 500, 500))
                backgroundLoc -= speed
                if backgroundLoc - speed <= speed:
                    backgroundLoc = 1500

                for event in pygame.event.get():
                    if (event.type == pygame.QUIT):
                        return
                    elif (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_RETURN):
                        if showSingleMode:
                            showSingleMode=False
                        elif showTimeMode:
                            showTimeMode=False
                        elif showPvpMode:
                            showPvpMode=False
                        elif selection == 1:
                            inSelectMenu=False
                            ship.initializeKeys()
                        elif selection == 2:
                            inSelectMenu=False
                            ship.initializeKeys()
                        elif selection == 3: # pvp 모드지?
                            inSelectMenu=False
                            ship.initializeKeys()
                            ship2.initializeKeys()
                        elif selection==4:
                            return
                    elif (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_w
                        and selection > 1
                        and not showSingleMode
                        and not showTimeMode
                        and not showPvpMode):
                        selection -= 1
                    elif (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_s
                        and selection < len(selectModeDict)
                        and not showSingleMode
                        and not showTimeMode
                        and not showPvpMode):
                        selection += 1
                selectPos = selectText.get_rect(topright=selectModeDict[selection].topleft)

                textOverlays = zip([singleText,timeText,pvpText,selectText,backText],[singlePos,timePos,pvpPos,selectPos,backPos])
                screen.blit(title, titleRect)
                for txt, pos in textOverlays:
                    screen.blit(txt, pos)
                
                pygame.display.flip()
         
         
#########################
#    Start Game Loop    #
#########################
    restart = True
    while restart == True:

        # Reset Sprite groups
        alldrawings = pygame.sprite.Group()
        allsprites = pygame.sprite.RenderPlain((ship,ship2))
        MasterSprite.allsprites = allsprites
        Alien.pool = pygame.sprite.Group(
            [alien() for alien in initialAlienTypes for _ in range(5)])
        Alien.active = pygame.sprite.Group()
        Missile.pool = pygame.sprite.Group([Missile() for _ in range(10)]) 
        Missile.active = pygame.sprite.Group()
        Explosion.pool = pygame.sprite.Group([Explosion() for _ in range(10)])
        Explosion.active = pygame.sprite.Group()

        # Reset game contents
        curTime = 0
        aliensThisWave, aliensLeftThisWave, Alien.numOffScreen = 10, 10, 10
        wave = 1
        doublemissile = False
        bombsHeld = 3
        score = 0
        doublemissile2 = False
        bombsHeld2 = 3
        score2 = 0
        missilesFired = 0
        powerupTime = 10 * clockTime
        powerupTimeLeft = powerupTime
        betweenWaveTime = 3 * clockTime
        betweenWaveCount = betweenWaveTime
        betweenDoubleTime = 8 * clockTime
        betweenDoubleCount = betweenDoubleTime
        betweenDoubleCount2 = betweenDoubleTime
        half_tf = True
        ship.alive = True
        ship2.alive = True

        # 본게임시작
        while ship.alive and ship2.alive :
            clock.tick(clockTime)

            if aliensLeftThisWave >= 20:
                powerupTimeLeft -= 1
            if powerupTimeLeft <= 0:
                powerupTimeLeft = powerupTime
                random.choice(powerupTypes)().add(powerups, allsprites)

        # Event Handling
            for event in pygame.event.get():
                if (event.type == pygame.QUIT
                    or event.type == pygame.KEYDOWN
                        and event.key == pygame.K_ESCAPE):
                    return
                # Ship Moving
                elif (event.type == pygame.KEYDOWN
                    and event.key in direction.keys()):
                    ship.horiz += direction[event.key][0] * speed
                    ship.vert += direction[event.key][1] * speed
                elif (event.type == pygame.KEYUP
                    and event.key in direction.keys()):
                    ship.horiz -= direction[event.key][0] * speed
                    ship.vert -= direction[event.key][1] * speed
                # Missile
                elif (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_SPACE):
                    if doublemissile :
                        Missile.position(ship.rect.topleft)
                        Missile.position(ship.rect.topright)
                        missilesFired += 2
                    else : 
                        Missile.position(ship.rect.midtop)
                        missilesFired += 1
                    if soundFX:
                        missile_sound.play()
                # Bomb
                elif (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_b):
                    if bombsHeld > 0:
                        bombsHeld -= 1
                        newBomb = ship.bomb()
                        newBomb.add(bombs, alldrawings)
                        if soundFX:
                            bomb_sound.play()

                elif (event.type == pygame.KEYDOWN
                    and event.key in direction2.keys()):
                    ship2.horiz += direction2[event.key][0] * speed
                    ship2.vert += direction2[event.key][1] * speed
                elif (event.type == pygame.KEYUP
                    and event.key in direction2.keys()):
                    ship2.horiz -= direction2[event.key][0] * speed
                    ship2.vert -= direction2[event.key][1] * speed
                # Missile
                elif (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_SPACE):
                    if doublemissile2 :
                        Missile.position(ship2.rect.topleft)
                        Missile.position(ship2.rect.topright)
                        missilesFired += 2
                    else : 
                        Missile.position(ship2.rect.midtop)
                        missilesFired += 1
                    if soundFX:
                        missile_sound.play()
                # Bomb
                elif (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_b):
                    if bombsHeld2 > 0:
                        bombsHeld2 -= 1
                        newBomb = ship2.bomb()
                        newBomb.add(bombs2, alldrawings)
                        if soundFX:
                            bomb_sound.play()

                # Pause
                elif (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_p):
                    pauseMenu = True
                    menuDict = {1: restartPos, 2: hiScorePos, 3: fxPos, 
                                4: musicPos, 5: helpPos, 6: quitPos}
                    
                    while pauseMenu:
                        clock.tick(clockTime)

                        screen.blit(
                            background, (0, 0), area=pygame.Rect(
                                0, backgroundLoc, 500, 500))    ## 이 3줄이 없으면 text업데이트가 안됨. why

                        for event in pygame.event.get():
                            if (event.type == pygame.QUIT):
                                return
                            elif (event.type == pygame.KEYDOWN  # unpause
                                and event.key == pygame.K_p):
                                pauseMenu = False
                            # Pause Menu
                            elif (event.type == pygame.KEYDOWN
                                and event.key == pygame.K_RETURN):
                                if showHiScores:
                                    showHiScores = False
                                elif selection == 1:    
                                    pauseMenu = False
                                    ship.alive = False
                                elif selection == 2:
                                    showHiScores = True
                                elif selection == 3:
                                    soundFX = not soundFX
                                    if soundFX:
                                        missile_sound.play()
                                    Database.setSound(int(soundFX))
                                elif selection == 4 and pygame.mixer:
                                    music = not music
                                    if music:
                                        pygame.mixer.music.play(loops=-1)
                                    else:
                                        pygame.mixer.music.stop()
                                    Database.setSound(int(music), music=True)
                                elif selection == 5:
                                    return
                                elif selection == 6:
                                    return
                            elif (event.type == pygame.KEYDOWN
                                and event.key == pygame.K_w
                                and selection > 1
                                and not showHiScores):
                                selection -= 1
                            elif (event.type == pygame.KEYDOWN
                                and event.key == pygame.K_s
                                and selection < len(menuDict)
                                and not showHiScores):
                                selection += 1
                            

                        selectPos = selectText.get_rect(topright=menuDict[selection].topleft)

                        if showHiScores:
                            textOverlays = zip(highScoreTexts, highScorePos)
                        else:
                            textOverlays = zip([restartText, hiScoreText, helpText, fxText,
                                                musicText, quitText, selectText,
                                                fxOnText if soundFX else fxOffText,
                                                musicOnText if music else musicOffText],
                                                [restartPos, hiScorePos, helpPos, fxPos,
                                                musicPos, quitPos, selectPos,
                                                fxOnPos if soundFX else fxOffPos,
                                                musicOnPos if music else musicOffPos])
                            screen.blit(pause, pauseRect)
                        for txt, pos in textOverlays:
                            screen.blit(txt, pos)

                        alldrawings.update()
                        pygame.display.flip()
                

        # Collision Detection
            # Aliens
            for alien in Alien.active:
                for bomb in bombs:
                    if pygame.sprite.collide_circle(
                            bomb, alien) and alien in Alien.active:
                        if alien.pType != 'white' :
                            alien.table()
                            Explosion.position(alien.rect.center)
                            aliensLeftThisWave, score = kill_alien(alien, aliensLeftThisWave, score)
                        missilesFired += 1
                        if soundFX:
                            alien_explode_sound.play()
                for bomb in bombs2:
                    if pygame.sprite.collide_circle(
                            bomb, alien) and alien in Alien.active:
                        if alien.pType != 'white' :
                            alien.table()
                            Explosion.position(alien.rect.center)
                            aliensLeftThisWave, score2 = kill_alien(alien, aliensLeftThisWave, score2)
                        if soundFX:
                            alien_explode_sound.play()
                for missile in Missile.active:
                    if pygame.sprite.collide_rect(
                            missile, alien) and alien in Alien.active:
                        missile.table()
                        if alien.pType != 'white' :
                            alien.table()
                            Explosion.position(alien.rect.center)
                            if alien.rect.center[0] < 500 :
                                aliensLeftThisWave, score = kill_alien(alien, aliensLeftThisWave, score)
                            else :
                                aliensLeftThisWave, score2 = kill_alien(alien, aliensLeftThisWave, score2)
                        if soundFX:
                            alien_explode_sound.play()
                if pygame.sprite.collide_rect(alien, ship):
                    if ship.shieldUp:
                        alien.table()
                        Explosion.position(alien.rect.center)
                        aliensLeftThisWave, score = kill_alien(alien, aliensLeftThisWave, score)
                        missilesFired += 1
                        ship.shieldUp = False
                    elif ship.life > 1:   # life
                        alien.table()
                        Explosion.position(alien.rect.center)
                        aliensLeftThisWave -= 1
                        score += 1
                        ship.life -= 1
                    else:
                        restart = False
                        ship.alive = False
                        ship.remove(allsprites)
                        Explosion.position(ship.rect.center)
                        if soundFX:
                            ship_explode_sound.play()
                if pygame.sprite.collide_rect(alien, ship2):
                    if ship2.shieldUp:
                        alien.table()
                        Explosion.position(alien.rect.center)
                        aliensLeftThisWave, score2 = kill_alien(alien, aliensLeftThisWave, score2)
                        missilesFired += 1
                        ship2.shieldUp = False
                    elif ship2.life > 1:   # life
                        alien.table()
                        Explosion.position(alien.rect.center)
                        aliensLeftThisWave -= 1
                        score2 += 1
                        ship2.life -= 1
                    else:
                        restart = False
                        ship2.alive = False
                        ship2.remove(allsprites)
                        Explosion.position(ship2.rect.center)
                        if soundFX:
                            ship_explode_sound.play()

            # PowerUps
            for powerup in powerups:
                if pygame.sprite.collide_circle(powerup, ship):
                    if powerup.pType == 'bomb':
                        bombsHeld += 1
                    elif powerup.pType == 'shield':
                        ship.shieldUp = True
                    elif powerup.pType == 'doublemissile' :
                        doublemissile = True
                    # elif powerup.pType == 'friendship' :
                    #     friendship = True 
                    #     miniship.alive = True   
                    powerup.kill()
                elif powerup.rect.top > powerup.area.bottom:
                    powerup.kill()
            for powerup in powerups:
                if pygame.sprite.collide_circle(powerup, ship2):
                    if powerup.pType == 'bomb':
                        bombsHeld2 += 1
                    elif powerup.pType == 'shield':
                        ship2.shieldUp = True
                    elif powerup.pType == 'doublemissile' :
                        doublemissile2 = True
                    # elif powerup.pType == 'friendship' :
                    #     friendship = True 
                    #     miniship.alive = True   
                    powerup.kill()
                elif powerup.rect.top > powerup.area.bottom:
                    powerup.kill()

        # Update Aliens
            if curTime <= 0 and aliensLeftThisWave > 0:
                Alien.position()
                curTime = alienPeriod
            elif curTime > 0:
                curTime -= 1

        # Update text overlays
            # if half_tf :
            #     waveText, leftText, scoreText, scoreText2, bombText, bombText2, ship1winText, ship2winText, drawText = ingame_text_update()
            # else :
            #     waveText, leftText, scoreText2, scoreText, bombText2, bombText, ship1winText, ship2winText, drawText = ingame_text_update()
            # font.render("Wave: " + str(wave), 1, WHITE),
    #             font.render("Aliens Left: " + str(aliensLeftThisWave), 1, WHITE),
    #             font.render("Score: " + str(score), 1, WHITE),
    #             font.render("Score: " + str(score2), 1, WHITE),
    #             font.render("Bombs: " + str(bombsHeld), 1, WHITE),
    #             font.render("Bombs: " + str(bombsHeld2), 1, WHITE),
    #             # font.render("Life: ", 1, WHITE)
    #             # font.render("Life: ", 1, WHITE)
    #             font.render('PLAYER 1 WIN!', 1, WHITE),
    #             font.render('PLAYER 2 WIN!', 1, WHITE),
    #             font.render('DRAW!', 1, WHITE)
            
            if half_tf :
                waveText = font.render("Wave: " + str(wave), 1, WHITE)
                leftText = font.render("Aliens: " + str(aliensLeftThisWave), 1, WHITE)
                scoreText = font.render("Score: " + str(score), 1, WHITE)
                scoreText2 = font.render("Score: " + str(score2), 1, WHITE)
                bombText = font.render("Bombs: " + str(bombsHeld), 1, WHITE)
                bombText2 = font.render("Bombs: " + str(bombsHeld2), 1, WHITE)
                lifeText = font.render("Life: ", 1, WHITE)
                lifeText2 = font.render("Life: ", 1, WHITE)
                ship1winText = font.render('PLAYER 1 WIN!', 1, WHITE)
                ship2winText = font.render('PLAYER 2 WIN!', 1, WHITE)
                drawText = font.render('DRAW!', 1, WHITE)
            else :
                waveText = font.render("Wave: " + str(wave), 1, WHITE)
                leftText = font.render("Aliens Left: " + str(aliensLeftThisWave), 1, WHITE)
                scoreText2 = font.render("Score: " + str(score2), 1, WHITE)
                bombText2 = font.render("Bombs: " + str(bombsHeld2), 1, WHITE)
                lifeText2 = font.render("Life: ", 1, WHITE)
                ship2winText = font.render('PLAYER 2 WIN!', 1, WHITE)
                drawText = font.render('DRAW!', 1, WHITE)

    
            wavePos = waveText.get_rect(topright=screen.get_rect().midtop)
            leftPos = leftText.get_rect(topleft=screen.get_rect().midtop)
            scorePos = scoreText.get_rect(topleft=screen.get_rect().bottomleft)
            # bombPos = bombText.get_rect(bottomleft=screen.get_rect().bottomleft)
            # lifePos = lifeText.get_rect(topleft=wavePos.bottomleft)
            scorePos2 = scoreText2.get_rect(topright=screen.get_rect().midbottom)
            # bombPos2 = bombText2.get_rect(bottomleft=screen.get_rect().midbottom)
            # lifePos2 = lifeText2.get_rect(topleft=wavePos.midbottom)
            ship1winPos = ship1winText.get_rect(center=screen.get_rect().center)
            ship2winPos = ship2winText.get_rect(center=screen.get_rect().center)
            drawPos = drawText.get_rect(center=screen.get_rect().center)

            text = [waveText, leftText, scoreText, scoreText2, bombText, bombText2, lifeText, lifeText2]
            # textposition = [wavePos, leftPos, scorePos, bombPos, lifePos, scorePos2, bombPos2, lifePos2]
            textposition = [wavePos, leftPos, scorePos, scorePos2]

            if doublemissile:
                if betweenDoubleCount > 0:
                    betweenDoubleCount -= 1
                elif betweenDoubleCount == 0:
                    doublemissile = False
                    betweenDoubleCount = betweenDoubleTime
            
            if doublemissile2:
                if betweenDoubleCount2 > 0:
                    betweenDoubleCount2 -= 1
                elif betweenDoubleCount2 == 0:
                    doublemissile2 = False
                    betweenDoubleCount = betweenDoubleTime
            
            # if friendship:
            #     if betweenDoubleCount > 0:
            #         betweenDoubleCount -= 1
            #     elif betweenDoubleCount == 0:
            #         friendship = False
            #         betweenDoubleCount = betweenDoubleTime

        # Detertmine when to move to next wave
            if aliensLeftThisWave <= 0:
                if betweenWaveCount > 0:
                    betweenWaveCount -= 1
                    nextWaveText = font.render(
                        'Wave ' + str(wave + 1) + ' in', 1, BLUE)
                    nextWaveNum = font.render(
                        str((betweenWaveCount // clockTime) + 1), 1, BLUE)
                    text.extend([nextWaveText, nextWaveNum])
                    nextWavePos = nextWaveText.get_rect(
                        center=screen.get_rect().center)
                    nextWaveNumPos = nextWaveNum.get_rect(
                        midtop=nextWavePos.midbottom)
                    textposition.extend([nextWavePos, nextWaveNumPos])
                    if wave % 4 == 0:
                        speedUpText = font.render('SPEED UP!', 1, RED)
                        speedUpPos = speedUpText.get_rect(
                            midtop=nextWaveNumPos.midbottom)
                        text.append(speedUpText)
                        textposition.append(speedUpPos)
                elif betweenWaveCount == 0:
                    if wave % 4 == 0:
                        speed += 0.5
                        MasterSprite.speed = speed
                        ship.initializeKeys()
                        ship2.initializeKeys()
                        aliensThisWave = 10
                        aliensLeftThisWave = Alien.numOffScreen = aliensThisWave
                    else:
                        aliensThisWave *= 2
                        aliensLeftThisWave = Alien.numOffScreen = aliensThisWave
                    if wave == 1:
                        Alien.pool.add([Fasty() for _ in range(5)])
                    if wave == 2:
                        Alien.pool.add([Roundy() for _ in range(5)])
                    if wave == 3:
                        Alien.pool.add([Crawly() for _ in range(5)])
                    wave += 1
                    betweenWaveCount = betweenWaveTime

            textOverlays = zip(text, textposition)

        # Update and draw all sprites and text
            # screen.blit(
            #     background, (0, 0), area=pygame.Rect(
            #         0, backgroundLoc, 500, 500))
            # backgroundLoc -= speed
            # if backgroundLoc - speed <= speed:
            #     backgroundLoc = 1500

            if half_tf:
                screen, background, backgroundLoc = background_update_half(screen, background, backgroundLoc)
            else:
                screen, background, backgroundLoc = background_update_half_two(screen, background, backgroundLoc)

            allsprites.update()
            allsprites.draw(screen)
            alldrawings.update()

            for txt, pos in textOverlays:
                screen.blit(txt, pos)

        # Update life
            # life1Rect.topleft = lifePos.topright
            life2Rect.topleft = life1Rect.topright
            life3Rect.topleft = life2Rect.topright

            if ship.life >= 3:
                screen.blit(life3, life3Rect)
            if ship.life >= 2:
                screen.blit(life2, life2Rect)
            if ship.life >= 1:
                screen.blit(life1, life1Rect)
            
            if ship2.life >= 3:
                screen.blit(life3, life3Rect)
            if ship2.life >= 2:
                screen.blit(life2, life2Rect)
            if ship2.life >= 1:
                screen.blit(life1, life1Rect)

            pygame.display.flip()


        # accuracy = round(score / missilesFired, 4) if missilesFired > 0 else 0.0
        # isHiScore = len(hiScores) < Database.numScores or score > hiScores[-1][1]
        # name = ''
        # nameBuffer = []


#########################
#    After Game Loop    #
#########################

    while True:
        clock.tick(clockTime)

        for event in pygame.event.get():
            if (event.type == pygame.QUIT):
                pygame.quit()
                sys.exit()
            # elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN :
            #     return scr_size, level_size, id, language

    # # Event Handling
    #     for event in pygame.event.get():
    #         if (event.type == pygame.QUIT
    #             or not isHiScore
    #             and event.type == pygame.KEYDOWN
    #                 and event.key == pygame.K_ESCAPE):
    #             return False
    #         elif (event.type == pygame.KEYDOWN
    #               and event.key == pygame.K_RETURN
    #               and not isHiScore):
    #             return True
    #         elif (event.type == pygame.KEYDOWN
    #               and event.key in Keyboard.keys.keys()
    #               and len(nameBuffer) < 8):
    #             nameBuffer.append(Keyboard.keys[event.key])
    #             name = ''.join(nameBuffer)
    #         elif (event.type == pygame.KEYDOWN
    #               and event.key == pygame.K_BACKSPACE
    #               and len(nameBuffer) > 0):
    #             nameBuffer.pop()
    #             name = ''.join(nameBuffer)
    #         elif (event.type == pygame.KEYDOWN
    #               and event.key == pygame.K_RETURN
    #               and len(name) > 0):
    #             Database().setScore(hiScores,name, score, accuracy)
    #             return True

    #     if isHiScore:
    #         hiScoreText = font.render('HIGH SCORE!', 1, RED)
    #         hiScorePos = hiScoreText.get_rect(
    #             midbottom=screen.get_rect().center)
    #         scoreText = font.render(str(score), 1, BLUE)
    #         scorePos = scoreText.get_rect(midtop=hiScorePos.midbottom)
    #         enterNameText = font.render('ENTER YOUR NAME:', 1, RED)
    #         enterNamePos = enterNameText.get_rect(midtop=scorePos.midbottom)
    #         nameText = font.render(name, 1, BLUE)
    #         namePos = nameText.get_rect(midtop=enterNamePos.midbottom)
    #         textOverlay = zip([hiScoreText, scoreText,
    #                            enterNameText, nameText],
    #                           [hiScorePos, scorePos,
    #                            enterNamePos, namePos])
    #     else:
    #         gameOverText = font.render('GAME OVER', 1, BLUE)
    #         gameOverPos = gameOverText.get_rect(
    #             center=screen.get_rect().center)
    #         scoreText = font.render('SCORE: {}'.format(score), 1, BLUE)
    #         scorePos = scoreText.get_rect(midtop=gameOverPos.midbottom)
    #         textOverlay = zip([gameOverText, scoreText],
    #                           [gameOverPos, scorePos])

    # Update and draw all sprites
        # ship1winPos = ship1winText.get_rect(center=screen.get_rect().center)
        # ship2winPos = ship2winText.get_rect(center=screen.get_rect().center)
        # drawPos = drawText.get_rect(center=screen.get_rect().center)

        # screen.blit(
        #     background, (0, 0), area=pygame.Rect(
        #         0, backgroundLoc, 500, 500))
        # backgroundLoc -= speed
        # if backgroundLoc - speed <= 0:
        #     backgroundLoc = 1500
        screen, background, backgroundLoc = background_update(screen, background, backgroundLoc)
        allsprites.update()
        allsprites.draw(screen)
        alldrawings.update()

        if ship.alive and not ship2.alive :
            screen.blit(ship1winText, ship1winPos)
        elif ship2.alive and not ship.alive :
            screen.blit(ship2winText, ship2winPos)
        elif not ship.alive and not ship2.alive :
            screen.blit(drawText, drawPos)

        elif ship.alive and ship2.alive :
            if score > score2 :
                screen.blit(ship1winText, ship1winPos)
            elif score < score2 :
                screen.blit(ship2winText, ship2winPos)
            elif score == score2 :
                screen.blit(drawText, drawPos)

        for txt, pos in textOverlay:
            screen.blit(txt, pos)
        pygame.display.flip()


if __name__ == '__main__':
    while(main()):
        pass