# Mahjong Generator

This is a customizable and easy-to-use backend system designed for mahjong enthusiasts from diverse regions and with various playing styles.

[Mahjong](https://en.wikipedia.org/wiki/Mahjong) is a game with numerous regional variants, but current mahjong systems tend to be specific to one type of mahjong and lack a unified platform that can accommodate different rules. This project aims to bridge that gap by providing a customizable framework that allows users to:

* **Define Options**: Tailor the mahjong rules to reflect local preferences or set your own, based on a range of customized options.

* **Generate Backends**: Create the backend logic automatically for mahjong games based on the given customized options set by the users.

* **Support Diversity**: Whether it's a widely played variant, a local favorite without an existing online platform, or some kind of rules negotiated by players of different Mahjong variants, Mahjong Generator makes these games accessible and playable.

## Installation

```sh
git clone https://github.com/yixiaoer/MahjongGenerator.git
cd MahjongGenerator
python3.12 -m venv venv
. venv/bin/activate
pip install mypy
```

## Basic Rules and Customized Options

To better represent the various rules in Mahjong Generator, we represent the rules of Mahjong itself and the rules that can be customized by user in the following two different ways:

1. *Basic Rules*: These include fundamental mechanics, logic, and elements that are essential for constructing any mahjong game. This category includes basic actions such as standard tile types, 'Chow', 'Pong', 'Kong', and 'Hu'.

2. *Customized Options*: These options enable the user to tailor the game mechanics to better fit their preferences or local variations, like the choice of tile types and the selection of special legal hands.

## Roadmap

- [ ] Basic Rules
    - [x] Draw tiles and discard tiles
    - [x] Hu, Kong, Pong, and Chow from discard
    - [x] Hu and Kong from wall
    - [ ] Joker
    - [ ] Special legal hands
    - [ ] Calculate score

- [ ] Customized Options
    - [x] Choice of tile types
    - [ ] Selection of special legal hands

## Glossary

* Shuffle tiles: 洗牌, Shuffle all face-down tiles.

* Build walls: 码牌, Every player takes N / 4 tiles (N is the total number of tiles)  and places them in a wall, 2 tiles high and N / 8 tiles long, at their position.

* Dealer: 庄家.

* Tile types.

    * Suited: 序数牌(also suit, 花色), divided into three suits(bamboo, characters, and dots) and each numbered from 1 to 9. The same tile appears 4 times in the set.

        - Bamboo: 条(also sticks, strings, 索子).

        - Characters: 万(also myriads).

        - Dots: 筒(also circles, coins, wheels, stones, 饼).

    * Honors: 字牌(also 番子). The same tile appears 4 times in the set.

        - Dragons: 箭牌(also 三元牌), include 3 types, red dragon(also red, 中), green dragon(also green, 发), and white dragon(also white, 白).

        - Winds: 风牌, include east(also 东, 东风), south(also 南, 南风), west(also 西, 西风), and north(also 北, 北风).

    * Bonus: 花牌. The same tile appears only once.

        - Flowers: 花牌, include plum blossom(also 梅), orchid(also 兰), chrysanthemum(also 菊), bamboo(also 竹).

        - Seasons: 季牌, include spring(also 春), summer(also 夏), autumn(also 秋), winter(also 冬).

* Joker: 混牌(also wildcard, wild card, 百搭, 癞子, 赖子, 鬼牌, 财神), can be used to represent any other tile needed to complete a sequence(meld or pair).

* Stack: 墩(also 栋, 垛): A single segment of the wall consisting of two tiles, one placed on top of the other.

* Chow: 吃 declared a chow from discord; 顺子 form a chow in hand.

* Pong / Pung: 碰 declared a pong from discord; 刻子, form a pong in hand.

* Kong: 杠, declared a kong; 杠子, form a pong in hand.

    * Concealed Kong: 暗杠, declared a kong with the player's own tiles.

    * Exposed kong: 明杠, declared a kong with a discarded tile.

    * Exposed kong from exposed pong: 加杠, already has a declared pong, later the player draws the 4th tile.

* Meld: Any form like Chow, Pong, Kong

* Pair: 将牌(also eyes, 雀头, 对子)

* Hu: 胡(also win, 和, 胡牌), call a win if complete a legal hand.

* Legal hand: 和牌牌型, the winning hand by either drawing one from the wall ("winning from the wall") or claiming a discard from another player("winning by discard").

    * Basic hands: four melds (a specific pattern of three pieces) + the eyes (a pair of identical pieces);

    * Special hands: can be different in variants as some exceptions.

* Ready hand: 听(also 听牌, 叫糊), the hand is one tile short of winning

## Some special legal hands

* All triplets: 对对胡(also all pongs or kongs, 对对和, 碰碰胡, 碰碰和, 大对子), consists of 4 pongs or kongs, and a pair.

* Mixed one suit: 混一色(also half flush, clean hand), tiles are one suit(bamboo, characters, or dots) and also some honor(winds or dragons) tiles.

* Pure one suit: 清一色(also full flush, pure suit hand), all tiles are the same suit(bamboo, characters, or dots).

* Seven pairs: 七对, hold seven pairs in hand.

* Dead wall draw: 杠上开花(also 岭上开花, 杠开), draw the winning tile off the dead wall after declaring a kong.

* Melded hand: 全求人, holds only one tile, with all other tiles declared as melds, and relies on a discard from another player to complete a pair.

* ...
