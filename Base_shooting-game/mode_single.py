import pygame
import random
import sys

from sprites import (MasterSprite, Ship, Alien, Missile, BombPowerup,
                     ShieldPowerup, DoublemissilePowerup, FriendPowerup, Explosion, LifePowerup,
                     Siney, Spikey, Fasty, Roundy, Crawly)
from database import Database
from load import load_image, load_sound, load_music
from menu import *

if not pygame.mixer:
    print('Warning, sound disablead')
if not pygame.font:
    print('Warning, fonts disabled')

BACK = 0

BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

direction = {None: (0, 0), pygame.K_UP: (0, -2), pygame.K_DOWN: (0, 2),
             pygame.K_LEFT: (-2, 0), pygame.K_RIGHT: (2, 0)}

class Single():
    def playGame():     # 창크기조절: 메인에서 기준size argument 받아오기 / 적용 : V 표시 
    # Initialize everything
        pygame.mixer.pre_init(11025, -16, 2, 512)
        pygame.init()
        screen_width = 500   # 스크린가로
        screen_height = 500  # 스크린세로
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Let's Kirin!")
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

    # Create the background which will scroll and loop over a set of different
        background = pygame.Surface((500, 2000))
        background = background.convert()
        background.fill((0, 0, 0))

    # Display the background
        screen.blit(background, (0, 0))
        pygame.display.flip()

    # Prepare background image
        # Game field
        field1, field1Rect = load_image("field.png")
        field2, field2Rect = load_image("field.png")
        field1Rect.midtop = screen.get_rect().midtop
        field2Rect.midbottom = field1Rect.midtop

        # Menu - pause 메뉴 Highscore & help
        menu, menuRect = load_image("menu.png")
        menuRect.midtop = screen.get_rect().midtop

        # pause
        pause,pauseRect = load_image('pause.png')
        pauseRect.midtop = screen.get_rect().midtop
        pauseMenu = False 

    # Prepare game objects
        # life
        life1, life1Rect = load_image('heart1.png')
        life2, life2Rect = load_image('heart2.png')
        life3, life3Rect = load_image('heart3.png')

        # Sounds
        missile_sound = load_sound('missile.ogg')
        bomb_sound = load_sound('bomb.ogg')
        alien_explode_sound = load_sound('alien_explode.ogg')
        ship_explode_sound = load_sound('ship_explode.ogg')
        load_music('music_loop.ogg')

        # font
        font = pygame.font.Font(None, 36)

    # Etc... 아래 루프에 넣어야하나
        speed = 1.5
        MasterSprite.speed = speed
        alienPeriod = 60 / speed
        clockTime = 60  # maximum FPS
        clock = pygame.time.Clock()
        ship = Ship()
        
        initialAlienTypes = (Siney, Spikey)
        # 수정
        powerupTypes = (BombPowerup, ShieldPowerup, DoublemissilePowerup, 
                        FriendPowerup, LifePowerup)
        
        bombs = pygame.sprite.Group()
        powerups = pygame.sprite.Group()


    # 데베 함수 메뉴 구현
        hiScores=Database().getScores()
        soundFX = Database().getSound()
        music = Database().getSound(music=True)
        if music and pygame.mixer: 
            pygame.mixer.music.play(loops=-1)
        # print(hiScores)
        # print(len(hiScores))
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
            highScoreTexts.extend([font.render(str(hs[x]), 1, BLACK)
                                for x in range(3)])
            highScorePos.extend([highScoreTexts[x].get_rect(
                topleft=highScorePos[x].bottomleft) for x in range(-3, 0)])

    # Temp - only load for Rect
        title, titleRect = load_image('title.png')
        titleRect.midtop = screen.get_rect().inflate(0, -200).midtop 
    
    # pause menu text  
        restartText = font.render('RESTART GAME', 1, BLACK)
        restartPos = restartText.get_rect(midtop=titleRect.inflate(0, 100).midbottom)  
        hiScoreText = font.render('HIGH SCORES', 1, BLACK)
        hiScorePos = hiScoreText.get_rect(topleft=restartPos.bottomleft)
        fxText = font.render('SOUND FX ', 1, BLACK)
        fxPos = fxText.get_rect(topleft=hiScorePos.bottomleft)
        fxOnText = font.render('ON', 1, RED)
        fxOffText = font.render('OFF', 1, RED)
        fxOnPos = fxOnText.get_rect(topleft=fxPos.topright)
        fxOffPos = fxOffText.get_rect(topleft=fxPos.topright)
        musicText = font.render('MUSIC', 1, BLACK)
        musicPos = fxText.get_rect(topleft=fxPos.bottomleft)
        musicOnText = font.render('ON', 1, RED)
        musicOffText = font.render('OFF', 1, RED)
        musicOnPos = musicOnText.get_rect(topleft=musicPos.topright)
        musicOffPos = musicOffText.get_rect(topleft=musicPos.topright)
        helpText=font.render('HELP',1,BLACK)
        helpPos=helpText.get_rect(topleft=musicPos.bottomleft)
        quitText = font.render('QUIT', 1, BLACK)
        quitPos = quitText.get_rect(topleft=helpPos.bottomleft)
        selectText = font.render('*', 1, BLACK)
        selectPos = selectText.get_rect(topright=restartPos.topleft)
        selection = 1
        showHiScores = False    


    #########################
    #    Start Time Mode    #
    #########################

        restart = True
        while restart == True:

        # Prepare game objects : reset
            # Reset Sprite groups
            alldrawings = pygame.sprite.Group()
            allsprites = pygame.sprite.RenderPlain((ship,))
            MasterSprite.allsprites = allsprites
            Alien.pool = pygame.sprite.Group(
                [alien() for alien in initialAlienTypes for _ in range(5)])
            Alien.active = pygame.sprite.Group()
            Missile.pool = pygame.sprite.Group([Missile() for _ in range(10)]) 
            Missile.active = pygame.sprite.Group()
            Explosion.pool = pygame.sprite.Group([Explosion() for _ in range(10)])
            Explosion.active = pygame.sprite.Group()

            # Reset game contents
            aliensThisWave, aliensLeftThisWave, Alien.numOffScreen = 10, 10, 10
            frienship = False
            doublemissile = False
            bombsHeld = 3
            score = 0
            missilesFired = 0
            wave = 1

            alienPeriod = clockTime // 2
            curTime = 0
            powerupTime = 8 * clockTime
            powerupTimeLeft = powerupTime
            betweenWaveTime = 3 * clockTime
            betweenWaveCount = betweenWaveTime
            betweenDoubleTime = 8 * clockTime
            betweenDoubleCount = betweenDoubleTime
            
            ship.alive = True
            ship.life = 3
            ship.initializeKeys()


        # 본게임시작
            while ship.alive:
                clock.tick(clockTime)

            # Drop Items
                if aliensLeftThisWave >= 10:
                    powerupTimeLeft -= 1
                if powerupTimeLeft <= 0:
                    powerupTimeLeft = powerupTime
                    random.choice(powerupTypes)().add(powerups, allsprites)

            # Event Handling
                for event in pygame.event.get():
                    if (event.type == pygame.QUIT
                        or event.type == pygame.KEYDOWN
                            and event.key == pygame.K_ESCAPE):
                        pygame.quit()
                        sys.exit()
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
                    # Pause Menu
                    elif (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_p):
                        pauseMenu = True
                        pauseMenuDict = {1: restartPos, 2: hiScorePos, 3: fxPos, 
                                    4: musicPos, 5: helpPos, 6: quitPos}
                        
                        while pauseMenu:
                            clock.tick(clockTime)

                            screen.blit(background, (0, 0))
                            screen.blit(pause, pauseRect)

                            for event in pygame.event.get():
                                if (event.type == pygame.QUIT
                                    or event.type == pygame.KEYDOWN
                                        and event.key == pygame.K_ESCAPE):
                                    pygame.quit()
                                    sys.exit()
                                elif (event.type == pygame.KEYDOWN  # unpause
                                    and event.key == pygame.K_p):
                                    pauseMenu = False
                                elif (event.type == pygame.KEYDOWN
                                    and event.key == pygame.K_RETURN):
                                    if showHiScores:
                                        showHiScores = False
                                    elif showHelp:
                                        showHelp=False
                                    elif selection == 1:    
                                        pauseMenu = False
                                        ship.alive = False
                                    elif selection == 2:
                                        showHiScores = True
                                    elif selection == 3:
                                        soundFX = not soundFX
                                        if soundFX:
                                            missile_sound.play()
                                        Database().setSound(int(soundFX))
                                    elif selection == 4 and pygame.mixer:
                                        music = not music
                                        if music:
                                            pygame.mixer.music.play(loops=-1)
                                        else:
                                            pygame.mixer.music.stop()
                                        Database().setSound(int(music), music=True)
                                    elif selection == 5:
                                        showHelp=True
                                    elif selection == 6:
                                        pygame.quit()
                                        sys.exit()
                                elif (event.type == pygame.KEYDOWN
                                    and event.key == pygame.K_UP
                                    and selection > 1
                                    and not showHiScores):
                                    selection -= 1
                                elif (event.type == pygame.KEYDOWN
                                    and event.key == pygame.K_DOWN
                                    and selection < len(pauseMenuDict)
                                    and not showHiScores):
                                    selection += 1
                                

                            selectPos = selectText.get_rect(topright=pauseMenuDict[selection].topleft)

                            if showHiScores:
                                # self.screen.blit(self.background, (0, 0))
                                img_menu, img_menuRect = load_image("menu.png")
                                img_menuRect.midtop = screen.get_rect().midtop
                                screen.blit(img_menu, img_menuRect)
                                textOverlays = zip(highScoreTexts, highScorePos)
                            elif showHelp:
                                # screen.blit(background, (0, 0))
                                img_menu, img_menuRect = load_image("pause.png") 
                                img_menuRect.midtop = screen.get_rect().midtop
                                screen.blit(img_menu, img_menuRect) 
                            else:
                                textOverlays = zip([restartText, hiScoreText, helpText, fxText,
                                                    musicText, quitText, selectText,
                                                    fxOnText if soundFX else fxOffText,
                                                    musicOnText if music else musicOffText],
                                                    [restartPos, hiScorePos, helpPos, fxPos,
                                                    musicPos, quitPos, selectPos,
                                                    fxOnPos if soundFX else fxOffPos,
                                                    musicOnPos if music else musicOffPos])
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
                    for missile in Missile.active:
                        if pygame.sprite.collide_rect(
                                missile, alien) and alien in Alien.active:
                            missile.table()
                            if alien.pType != 'white' :
                                alien.table()
                                Explosion.position(alien.rect.center)
                                aliensLeftThisWave, score = kill_alien(alien, aliensLeftThisWave, score)
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

                # PowerUps
                for powerup in powerups:
                    if pygame.sprite.collide_circle(powerup, ship):
                        if powerup.pType == 'bomb':
                            bombsHeld += 1
                        elif powerup.pType == 'shield':
                            ship.shieldUp = True
                        elif powerup.pType == 'doublemissile' :
                            doublemissile = True
                        elif powerup.pType == 'friendship' :
                            friendship = True
                        elif powerup.pType == 'life':
                            if ship.life < 3:
                                ship.life += 1    
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
                waveText = font.render("Wave: " + str(wave), 1, BLACK)
                leftText = font.render("Bears Left: " + str(aliensLeftThisWave), 1, BLACK)
                scoreText = font.render("Score: " + str(score), 1, BLACK)
                bombText = font.render("Fart Bombs: " + str(bombsHeld), 1, BLACK)

                wavePos = waveText.get_rect(topleft=screen.get_rect().topleft)
                leftPos = leftText.get_rect(midtop=screen.get_rect().midtop)
                scorePos = scoreText.get_rect(topright=screen.get_rect().topright)
                bombPos = bombText.get_rect(bottomleft=screen.get_rect().bottomleft)

                text = [waveText, leftText, scoreText, bombText]
                textposition = [wavePos, leftPos, scorePos, bombPos]

                if doublemissile:
                    if betweenDoubleCount > 0:
                        betweenDoubleCount -= 1
                    elif betweenDoubleCount == 0:
                        doublemissile = False
                        betweenDoubleCount = betweenDoubleTime

            # Detertmine when to move to next wave
                if aliensLeftThisWave <= 0:
                    if betweenWaveCount > 0:
                        betweenWaveCount -= 1
                        nextWaveText = font.render(
                            'Wave ' + str(wave + 1) + ' in', 1, BLACK)
                        nextWaveNum = font.render(
                            str((betweenWaveCount // clockTime) + 1), 1, BLACK)
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

            # moving field
                field1Rect.y += 2 # speed? float(x) / int(o)
                field2Rect.y += 2
                if field1Rect.y >= screen_height:
                    field1Rect.midbottom = field2Rect.midtop
                if field2Rect.y >= screen_height:
                    field2Rect.midbottom = field1Rect.midtop
                screen.blit(field1, field1Rect)
                screen.blit(field2, field2Rect)

            # Update and draw all sprites and text                                   
                allsprites.update()
                allsprites.draw(screen)
                alldrawings.update()
                for txt, pos in textOverlays:
                    screen.blit(txt, pos)

            # Update life
                life1Rect.topleft = wavePos.bottomleft
                life2Rect.topleft = wavePos.bottomleft
                life3Rect.topleft = wavePos.bottomleft

                if ship.life == 3:
                    screen.blit(life3, life3Rect)
                elif ship.life == 2:
                    screen.blit(life2, life2Rect)
                elif ship.life == 1:
                    screen.blit(life1, life1Rect)

                pygame.display.flip()


            accuracy = round(score / missilesFired, 4) if missilesFired > 0 else 0.0
            isHiScore = len(hiScores) < Database().numScores or score > hiScores[-1][1]
            name = ''
            nameBuffer = []


    #########################
    #    After Game Loop    #
    #########################

        while True:
            clock.tick(clockTime)

        # Event Handling
            for event in pygame.event.get():
                if (event.type == pygame.QUIT
                    or not isHiScore
                    and event.type == pygame.KEYDOWN
                        and event.key == pygame.K_ESCAPE):
                    return False
                elif (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_RETURN
                    and not isHiScore):
                    return True
                elif (event.type == pygame.KEYDOWN
                    and event.key in Keyboard.keys.keys()
                    and len(nameBuffer) < 8):
                    nameBuffer.append(Keyboard.keys[event.key])
                    name = ''.join(nameBuffer)
                elif (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_BACKSPACE
                    and len(nameBuffer) > 0):
                    nameBuffer.pop()
                    name = ''.join(nameBuffer)
                elif (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_RETURN
                    and len(name) > 0):
                    Database().setScore(hiScores,name, score, accuracy)
                    return True  

            if isHiScore:
                hiScoreText = font.render('SCORE', 1, RED)
                hiScorePos = hiScoreText.get_rect(
                    midbottom=screen.get_rect().center)
                scoreText = font.render(str(score), 1, BLACK)
                scorePos = scoreText.get_rect(midtop=hiScorePos.midbottom)
                enterNameText = font.render('ENTER YOUR NAME:', 1, RED)
                enterNamePos = enterNameText.get_rect(midtop=scorePos.midbottom)
                nameText = font.render(name, 1, WHITE)
                namePos = nameText.get_rect(midtop=enterNamePos.midbottom)
                textOverlay = zip([hiScoreText, scoreText,
                                enterNameText, nameText],
                                [hiScorePos, scorePos,
                                enterNamePos, namePos])
            else:
                gameOverText = font.render('GAME OVER', 1, BLACK)
                gameOverPos = gameOverText.get_rect(
                    center=screen.get_rect().center)
                scoreText = font.render('SCORE: {}'.format(score), 1, BLACK)
                scorePos = scoreText.get_rect(midtop=gameOverPos.midbottom)
                textOverlay = zip([gameOverText, scoreText],
                                [gameOverPos, scorePos])

        # moving field         
            field1Rect.y += 2 # speed? float(x) / int(o)
            field2Rect.y += 2
            if field1Rect.y >= screen_height:
                field1Rect.midbottom = field2Rect.midtop
            if field2Rect.y >= screen_height:
                field2Rect.midbottom = field1Rect.midtop

            screen.blit(field1, field1Rect)
            screen.blit(field2, field2Rect)

        # Update and draw all sprites
            allsprites.update()
            allsprites.draw(screen)
            alldrawings.update()
            for txt, pos in textOverlay:
                screen.blit(txt, pos)

            pygame.display.flip()
