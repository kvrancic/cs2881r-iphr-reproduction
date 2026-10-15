"""The whole deck as one Timeline, act by act. ../storyboard.md describes the same slides in words."""
from timeline import Timeline
from story.s1_claim import act1
from story.s2_did import act2
from story.s3_kind import act3
from story.s4_ext import act4
from story.s5_close import act5


def story():
    tl = Timeline()
    act1(tl)      # title, the Figure 1 example, the pairs, Figure 2
    act2(tl)      # four things; 1 the recompute, 2 the rerun
    act3(tl)      # 3 Figure 2 split by kind of question
    act4(tl)      # 4 the two variations: fact cards, then the wording of geography questions
    act5(tl)      # what Figure 2 measures, thank you
    return tl
