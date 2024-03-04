┌─┬┬─┬─┐┌──┐           ┌┐
││││┼│┌┘│┌─┼─┬─┬┬─┬┬┬─┐│└┬─┬┬┐
││││┌┤└┐│└┐│┴┤│││┴┤┌┤┼└┤┌┤┼│┌┘
└┴─┴┘└─┘└──┴─┴┴─┴─┴┘└──┴─┴─┴┘
Read Me
For cod version: v.0.0.1

Welcome to the NPC Generator!
First, thank you for using this little program, and I hope you like it.

table of contents:
------------------------------------------------------------------------------------------------------------------------
Basic terminology.....................................................Line...23
WARNING...............................................................Line...39
Instructions how to add stuff.........................................Line...50
    - config..........................................................Line...55
    - database........................................................Line...84
Standard documents....................................................Line..107
    - config.txt......................................................Line..111
    - database.txt....................................................Line..182
------------------------------------------------------------------------------------------------------------------------

__Basic terminology__
terminator                  -   refers to '/end'
group heading               -   refers to word between two sets of '__' for example '__Name__'
group                       -   refers to everything between group heading and terminator also refers to name of group
                                from database.txt while explaining how stuff inside config.txt work
parameter                   -   refers to single line inside of group
choosing pool               -   every time some parameter is chosen on random it draws it from choosing pool
rarity                      -   sometimes called rarity class refers to how often parameter is in choosing pool
optional group              -   refers to groups that have less than 100% of being in choosing pool for groups
multiple group              -   refers to groups that have chance of having more than one parameter
conditioned group heading   -   refers to word between two sets of '==' for example '==FemaleName=='
conditioned group           -   refers to groups that depend on parameters of other groups,
                                also refers to everything between conditioned group heading heading and terminator
influential group           -   refers to groups from which parameter influences conditioned group
------------------------------------------------------------------------------------------------------------------------

__WARNING__
These must be in the same folder as runnable version of program: config.txt, database.txt, save.txt
Inside config.txt do not change order or amount of groups
Check that config.txt and database.txt are supported by your version of NPC generator
    (type help in NPC generator to get version)
Follow all the rules listed in config.txt while modifying it
While programming new features for NPC generator make sure order of groups in config.txt is compatible
Not following rules or poor coding skills from programmer side could lead to crashes so be considerate
Do not try to extinguish electrical fire with water when your CPU melts down (or ever)
------------------------------------------------------------------------------------------------------------------------

__Instructions how to add stuff__
Do you want to add rhino as a potential race for your NPC, do you want to crate animal companion instead of humanoid or
do you just want to have the most detailed and thought out NPC-s the world has ever seen? Well for everything except the
last part you can use this tool. Just be sure to follow guidelines given below and only imagination is your limit.

    ==config==
    Inside of config.txt are all the rules for generating NPC-s. Here you can modify:

        __Rarity__          :   between group heading and terminator you can add up to three of any letter and number
                                which will give name to your rarity class. Follow that with '_by_' and any number
                                from 0 to 100 which symbolizes chance in percentage of parameter being in choosing pool.
                                To assign rarity class to a parameter in database.txt you need to write name of rarity
                                class (or number from 0 to 100) inside of parentheses at the end of parameter.

        __OptionalGroup__   :   between group heading and terminator you can add name of groups that you want to be
                                optional groups. Follow that with '_by_' and any number from 0 to 100 which symbolizes
                                chance in percentage of group being in choosing pool. If you don't want any group to be
                                optional write 'None'.

        __MultipleGroup__   :   between group heading and terminator you can add name of groups that you want to be
                                multiple groups. Follow that with '_by_', any number from 0 to 100 which symbolizes
                                chance in percentage of group having additional parameter, '_' and 'min' with minimum
                                number of parameters for that group next to it without space, then 'max' followed by
                                maximum number of parameters for that group without spaces. If you don't want any group
                                to be multiple just write 'None'.

        __ConditionedGroup__:   between group heading and terminator you can add: name of a conditioned group followed
                                by '_by_' and then the name of a group influencing your conditioned group.
                                Make sure you separate them with '_', also make sure you list them
                                in order that is logical to you, and which is NOT circular in logic. If some group is
                                conditioned by a group that is already conditioned by some other group, ensure that
                                influential group is above conditioned group. More about how to implement it in database
                                part of this file. If you don't want any group to be conditioned write 'None'.

    ==database==
    Inside of database.txt are all nitty and gritty parts of this magical generator. Here you can let your imagination
    loose. Unlike config.txt, this part has less rules but more substance. It is divided into two sections: groups and
    conditioned groups. So without further ado here is what you need to do. Stand on your toe and say juhuhu... JK:

        __Group__           :   type double underscore '__' followed by any name you want, just be sure you use ONLY
                                letters and/or numbers, NO special characters or white space characters and finish it
                                off with double underscore '__' (essentially make group heading and give it any name you
                                want). Once you have group heading, put in your text. That are your parameters for
                                character. You can give parameters a rarity class. Parameters MUST be listed one under
                                another. Long story short, press enter ('\n' for programmers) then start typing your
                                new parameter. Once you feel like you have enough, put terminator '/end'.
                                Congratulations! You just made your own group. There is no limit for number of groups
                                and/or parameters inside of groups. At least not one I know off...

        __ConditionedGroup__:   type double equal sign '==' followed by name of parameter from influential group
                                in order that you listed group names in ConditionedGroup inside of config.txt. Finish
                                it by typing name of conditioned group and double equal sign '=='. Once you have a
                                heading same rules apply as for groups. Only one more thing - if one parameter is
                                present in multiple conditioned groups and/or the original group, rarity class from
                                parameter that is in the most specific conditioned group will be one that is applied.
------------------------------------------------------------------------------------------------------------------------

__Standard documents__
Because we all F*** up sometimes, here are original files that will work. A reset-to-factory-settings button, so to say.


                                                ==config.txt==

## last edit: 3.3.2024.
## cod version compatible: v.0.0.1
------------------------------------------------------------------------------------------------------------------------
## WARNING
## adding new groups to config.txt causes changes in code!!
## be careful in which order you place and program new groups
------------------------------------------------------------------------------------------------------------------------

## parameter has chance of being in choosing pool equal to number after 'by' in percentage
## parameter can have rarity class in form of number from 0 to 100 which has no need to be specified
## if parameter has no rarity, rarity 100% is automatically given to it
## in database.txt parameter has its rarity writen in following form ( 'Parameter(S)' )
## example: S_by_100

__Rarity__
S_by_100
C_by_80
U_by_50
R_by_30
M_by_10
/end
------------------------------------------------------------------------------------------------------------------------

## optional group has chance of occurring equal to number after 'by' in percentage
## Fear_by_80 has 80% chance of occurring in character
## example: Fear_by_80

__OptionalGroup__
Characteristics_by_95
/end
------------------------------------------------------------------------------------------------------------------------

## group can both be optional and multiple
## multiple group has a chance of being multiplied equal to number after 'by' in percentage
## multiple group will occur minimum of 'min' times and maximum of 'max' times
## Race_by_20_min1max4 has 20% chance of occurring 2 times, 4% chance of occurring 3 times,
## 0.8% chance of occurring 4 times
## example: Race_by_20_min1max2

__MultipleGroup__
Race_by_20_min1max2
Characteristics_by_50_min1max4
/end
------------------------------------------------------------------------------------------------------------------------

## conditioned group will match with all and any of its conditions
## Name_by_Sex_Race -> ( Name ; SexName ; RaceName ; SexRaceName )
## if a character has 2 or more parameters in a influential group, all of them will be taken in account
## if the same parameter is in 2 or more groups, rarity class of one that is in more specific group will be taken
## if some parameter is in 2 or more groups that are equally specific, rarity class will be taken randomly from one of
## those groups
## conditioned group MUST be named in particular order: if you condition your group Name by group Sex then group Race,
## your conditioned group must be named SexRaceName
## in database Name_by_Sex_Race should look like: ( MaleHumanName / FemaleDwarfName / MaleName / ElfName ... )
## conditioned groups can not be all conditioned by each other - no circular logic
## if conditioned group is conditioned by another conditioned group, the one which is also influential must go above
## EXAMPLES FOR THE ABOVE: NO ( Name_by_Sex_Race ; Race_by_Name ... ) OR ( Name_by_Sex_Race ; Race_by_Sex ... )
## CAN DO ( Race_by_Sex ; Name_by_Sex_Race ... )
## in database.txt keep original group in a spot in which you want it to print out, but put all of its conditioned
## variants in (## ConditionedGroup) section of the database.txt
## example: Name_by_Sex_Race

__ConditionedGroup__
Sex_by_Race
Name_by_Sex_Race
/end
------------------------------------------------------------------------------------------------------------------------


                                                ==database.txt==

## last edit: 3.3.2024.
## cod version compatible: v.0.0.1
------------------------------------------------------------------------------------------------------------------------

__Name__
Stave
Rocky
Martin(R)
/end
------------------------------------------------------------------------------------------------------------------------

__Sex__
Male
Female
NonBinary(R)
/end
------------------------------------------------------------------------------------------------------------------------

__Race__
Dwarf
Elf
Gnome
Halfling
Human
Azarketi(U)
Catfolk(U)
Fatchling(U)
Gnoll(U)
Grippli(U)
Hobgoblin(U)
Kitsune(U)
Kobold(U)
Leshy(U)
Lizardfolk(U)
Nagaji(U)
Orc(U)
Ratfolk(U)
Tengu(U)
Vanara(U)
Anadi(R)
Android(R)
Automaton(R)
Conrasu(R)
Fleshwrap(R)
Ghoran(R)
Goloma(R)
Kashrishi(R)
Poppet(R)
Shisk(R)
Shoony(R)
Skeleton(R)
Sprite(R)
Strix(R)
Vishkanya(R)
/end
------------------------------------------------------------------------------------------------------------------------

__Characteristics__
Likes to wear dresses
fears rats
loves to walk around at night
insane
funny
loves their job
hates their job
has big family
has a harem
has too many pets
acts like a child
brave
/end
------------------------------------------------------------------------------------------------------------------------



------------------------------------------------------------------------------------------------------------------------
## ConditionedGroup ----------------------------------------------------------------------------------------------------
------------------------------------------------------------------------------------------------------------------------

==MaleName==
Martin(S)
/end
------------------------------------------------------------------------------------------------------------------------

==AndroidSex==
Male(1)
Female(1)
NonBinary
/end
------------------------------------------------------------------------------------------------------------------------

==AutomatonSex==
Male(1)
Female(1)
NonBinary
/end
------------------------------------------------------------------------------------------------------------------------
