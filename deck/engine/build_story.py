"""The whole deck as one Timeline, act by act. ../storyboard.md describes the same slides in words."""
from timeline import Timeline
from story.s1_claim import act1
from story.s2_did import act2
from story.s3_why import act3
from story.s4_ext import act4
from story.s5_close import act5


def story():
    tl = Timeline()
    act1(tl)      # title, the Figure 1 example, the pairs, Figure 2
    act2(tl)      # three things: the recompute and the rerun
    act3(tl)      # what produces the flags: the guess-with-a-lean model
    act4(tl)      # the two extensions: fact cards and exact wording
    act5(tl)      # what Figure 2 measures, thank you
    return tl
