
import math
import cjb.uif

from cjb.uif.layout import Size, Grid, Rect, layoutInScroller
from viz.scenes.base import BaseScene
from viz.scenes.pair import PairScene, RawPairScene
from viz.layout import buttonSize

from spats_shape_seq.pair import Pair



class Nuc(object):

    def __init__(self, char, idx, context):
        self.char = char
        self.idx = idx
        self.context = context

    @property
    def displayName(self):
        return self.char


class MatchedPair(object):

    def __init__(self, r1, r2, multiplicity, rowid, identifier):
        self.r1 = r1
        self.r2 = r2
        self.r1_nucs = [ Nuc(r1[idx], idx, self) for idx in range(len(r1)) ]
        self.r2_nucs = [ Nuc(r2[idx], idx, self) for idx in range(len(r2)) ]
        self.multiplicity = multiplicity
        self.rowid = rowid
        self.identifier = identifier

    def display_id(self):
        return ":".join(self.identifier.split(':')[-2:])

    #@property
    #def displayName(self):
    #    return self.r1 + "   " + self.r2


class Matches(BaseScene):

    def __init__(self, ui, include_tags = None, exclude_tags = None, site = None):
        self.include_tags = include_tags
        self.exclude_tags = exclude_tags
        self.site = site
        self.match_filter = ""
        BaseScene.__init__(self, ui, self.__class__.__name__)

    def addMatchView(self, matched_pair):
        v = cjb.uif.views.View(obj = matched_pair)
        v.name_label = v.addSubview(cjb.uif.views.Label(str(matched_pair.display_id()), fontSize = 11))
        v.mult_bar = v.addSubview(cjb.uif.views.View())
        v.mult_bar.bg = "bar"
        v.mult_label = v.addSubview(cjb.uif.views.Label(str(matched_pair.multiplicity), fontSize = 11))
        v.mult_label.alignment = "right"
        v.mult_percent = v.addSubview(cjb.uif.views.Label("{:.2f}%".format(100.0 * matched_pair.multiplicity / float(self.total_matches)), fontSize = 11))
        v.bg = "light_grey"

        tagged_pair = self.processed_pair(matched_pair)

        colors = self.ui.colors
        target = tagged_pair.target
        bg = colors.color("grey")
        tcol = colors.color("target")
        nomatch_col = colors.color("grey")
        error_col = colors.color("error")

        v.r1_nucs = []
        for nuc in matched_pair.r1_nucs:
            tag = None
            bg = nomatch_col
            for tag in tagged_pair.r1.tags:
                if nuc.idx >= tag[1] and nuc.idx < tag[1] + tag[2]:
                    bg = colors.color(tag[0].rstrip("_rc"))
                    break
            if nuc.idx in tagged_pair.r1.match_errors or nuc.idx in tagged_pair.r1.adapter_errors:
                bg = error_col
            nv = cjb.uif.views.Button(obj = nuc)
            nv.sideSpacing = 0
            nv.bg = bg
            v.addSubview(nv)
            self.addView(nv)
            v.r1_nucs.append(nv)

        v.r2_nucs = []
        for nuc in matched_pair.r2_nucs:
            tag = None
            bg = nomatch_col
            for tag in tagged_pair.r2.tags:
                if nuc.idx >= tag[1] and nuc.idx < tag[1] + tag[2]:
                    bg = colors.color(tag[0].rstrip("_rc"))
                    break
            if nuc.idx in tagged_pair.r2.match_errors or nuc.idx in tagged_pair.r2.adapter_errors:
                bg = error_col
            nv = cjb.uif.views.Button(obj = nuc)
            nv.sideSpacing = 0
            nv.bg = bg
            v.addSubview(nv)
            self.addView(nv)
            v.r2_nucs.append(nv)

        v.target = matched_pair
        self.addView(v)
        return v

    def build(self):
        BaseScene.build(self)
        if self.site:
            pairs = self.ui.db.results_matching_site(self.ui.result_set_id, self.site.target_id, self.site.end, self.site.site, limit = 50)
            self.total_matches = self.site.total
        else:
            pairs = self.ui.db.results_matching(self.ui.result_set_id, self.include_tags, self.exclude_tags, limit = 50)
            self.total_matches = self.ui.db.count_matches(self.ui.result_set_id, self.include_tags, self.exclude_tags)
        matches = [ MatchedPair(p[2], p[3], p[4], p[0], p[1]) for p in pairs ]
        self.matchViews = [ self.addMatchView(m) for m in matches ]
        self.filter_label = self.addView(cjb.uif.views.Label("Filter: <None>", fontSize = 11))

    def layoutMatch(self, view):
        grid = Grid(frame = view.frame.bounds(), itemSize = Size(10, 16), columns = 100, rows = 1)
        grid.setLocation(12, 0)
        grid.applyToViews(view.r1_nucs)
        grid.setLocation(50, 0)
        grid.applyToViews(view.r2_nucs)
        view.name_label.frame = grid.frame(0, 10)
        view.mult_label.frame = grid.frame(88, 10)
        f = grid.frame(88, 12)
        # take the 4th root, since most of these will be very small as a straight % of total
        factor = math.sqrt(math.sqrt((float(view.obj.multiplicity) / float(self.total_matches))))
        f.update(origin = f.origin, w = int(factor * float(f.size.width)), h = f.size.height)
        view.mult_bar.frame = f
        view.mult_percent.frame = grid.frame(88, 10)


    def layout(self, view):
        BaseScene.layout(self, view)
        cur = view.frame.centeredSubrect(w = 1000, h = view.frame.size.h - 100)
        self.scroller = layoutInScroller(self.matchViews, cur, Size(1000, 14), 2, self.scroller)
        for v in self.matchViews:
            self.layoutMatch(v)
        self.filter_label.frame = view.frame.topLeftSubrect(w = 200, h = 20, margin = 20)
        return view

    def processed_pair(self, matched_pair):
        pair = Pair()
        pair.set_from_data(matched_pair.identifier, matched_pair.r1, matched_pair.r2, matched_pair.multiplicity)
        self.ui.processor.process_pair_detail(pair)
        return pair
        
    def update_filter(self):
        f = self.match_filter
        for v in self.matchViews:
            p = v.obj
            hidden = (f and f not in p.r1 and f not in p.r2)
            if v.hidden != hidden:
                v.hidden = hidden
                self.sendViewMessage(v, "hide" if hidden else "show")
        self.sendViewMessage(self.filter_label, "setText", "Filter: {}".format(self.match_filter or "<None>"))

    def handleViewMessage(self, scene, obj, message):
        if obj and (isinstance(obj, MatchedPair) or isinstance(obj, Nuc)):
            mp = obj if isinstance(obj, MatchedPair) else obj.context
            pair = self.processed_pair(mp)
            if pair.has_site:
                self.ui.pushScene(PairScene(self.ui, pair, expanded = True))
            else:
                self.ui.pushScene(RawPairScene(self.ui, pair, expanded = True))
        else:
            BaseScene.handleViewMessage(self, scene, obj, message)

    def handleKeyEvent(self, keyInfo):
        if keyInfo.get("s") == "DEL":
            self.match_filter = self.match_filter[:-1]
            self.update_filter()
        elif keyInfo.get("t") in [ "a","c","g","t" ] and 1 == len(keyInfo):
            self.match_filter += keyInfo["t"].upper()
            self.update_filter()
        elif keyInfo.get("t") == "x" and 1 == len(keyInfo):
            self.match_filter = ""
            self.update_filter()
        else:
            BaseScene.handleKeyEvent(self, keyInfo)

