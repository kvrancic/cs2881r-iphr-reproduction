"""The whole deck as one Timeline, act by act. storyboard.md describes the same slides in words."""
from timeline import Timeline
from story.act1 import act1
from story.act2 import act2, act3
from story.act4 import act_videos_1, act_videos_2, act4
from story.act5 import act5, act6


def story():
    tl = Timeline()
    act1(tl)            # 1-16   cold open
    act_videos_1(tl)    # 17     Video 1
    act2(tl)            # 18-26  the castle
    act3(tl)            # 27-31  read versus write
    act_videos_2(tl)    # 32-33  Video 2, parts one and two
    act4(tl)            # 34-40  results
    act5(tl)            # 41-49  where this goes
    act6(tl)            # 50-57  why us, the close
    return tl
