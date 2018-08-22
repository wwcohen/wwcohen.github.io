#!/bin/csh

foreach m (*.mpg)
    mpeg_play $m -geometry - +100+100	
end