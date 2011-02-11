#-------------------------------------------------------------------------------
# Name:         romanText/translate.py
# Purpose:      Translation routines for roman numeral analysis text files
#
# Authors:      Christopher Ariza
#               Michael Scott Cuthbert
#
# Copyright:    (c) 2011 The music21 Project
# License:      LGPL
#-------------------------------------------------------------------------------


'''Translation routines for roman numeral analysis text files, as defined and demonstrated by Dmitri Tymoczko.
'''
import unittest
import music21
import copy


from music21.romanText import base as romanTextModule

from music21 import environment
_MOD = 'romanText.translate.py'
environLocal = environment.Environment(_MOD)



def romanTextToStreamScore(rtHandler, inputM21=None):
    '''Given a roman text handler, return or fill a Score Stream.
    '''
    # this could be just a Stream, but b/c we are creating metadata, perhaps better to match presentation of other scores. 

    from music21 import metadata
    from music21 import stream
    from music21 import note
    from music21 import meter
    from music21 import key
    from music21 import roman
    from music21 import tie


    if inputM21 == None:
        s = stream.Score()
    else:
        s = inputM21

    # metadata can be first
    md = metadata.Metadata()
    s.insert(0, md)

    p = stream.Part()
    # ts indication are found in header, and also found elsewhere
    tsCurrent = None # store initial time signature
    tsSet = False # store if set to a measure
    lastMeasureNumber = 0
    previousChord = None
    
    for t in rtHandler.tokens:
        if t.isTitle():
            md.title = t.data            
        elif t.isWork():
            md.alternativeTitle = t.data
        elif t.isComposer():
            md.composer = t.data
        elif t.isTimeSignature():
            tsCurrent = meter.TimeSignature(t.data)
            tsSet = False
            environLocal.printDebug(['tsCurrent:', tsCurrent])
            
        elif t.isMeasure():
            if t.variantNumber is not None:
                environLocal.printDebug(['skipping variant: %s' % t])
                continue
            # pass this off to measure creation tools
            if (t.number[0] > lastMeasureNumber + 1) and (previousChord is not None):
                for i in range(lastMeasureNumber + 1, t.number[0]):
                    fillM = stream.Measure()
                    fillM.number = i
                    newRn = copy.deepcopy(previousChord)
                    newRn.lyric = ""
                    newRn.duration = copy.deepcopy(tsCurrent.barDuration)
                    if previousChord.tie == None:
                        previousChord.tie = tie.Tie('start')
                    else:
                        previousChord.tie.type = 'continue'

                    newRn.tie = tie.Tie('stop')
                    previousChord = newRn
                    
                    fillM.append(newRn)
                    p.append(fillM)
                lastMeasureNumber = t.number[0] - 1
            m = stream.Measure()
            if not tsSet:
                m.timeSignature = tsCurrent
                tsSet = True # only set when changed

            if len(t.number) == 1: # if not a range
                m.number = t.number[0]
                lastMeasureNumber = t.number[0]
            else:
                lastMeasureNumber = t.number[1]
                environLocal.printDebug(['cannot yet handle measure tokens defining measure ranges: %s' % t.number])

            o = 0.0 # start offsets at zero
            previousChordInMeasure = None
            for i, a in enumerate(t.atoms):
                if isinstance(a, romanTextModule.RTKey):
                    kCurrent = a.getKey()

                if isinstance(a, romanTextModule.RTBeat):
                    # set new offset based on beat
                    o = a.getOffset(tsCurrent)
                    if previousChordInMeasure is None and previousChord is not None:
                        # setting a new beat before giving any chords
                        firstChord = copy.deepcopy(previousChord)
                        firstChord.quarterLength = o
                        firstChord.lyric = ""
                        if previousChord.tie == None:
                            previousChord.tie = tie.Tie('start')
                        else:
                            previousChord.tie.type = 'continue'    
                        firstChord.tie = tie.Tie('stop')
                        previousChord = firstChord
                        previousChordInMeasure = firstChord
                        m.insert(0, firstChord)
                        
                if isinstance(a, romanTextModule.RTChord):
                    # probably best to find duration
                    if previousChordInMeasure is None:
                        pass # use default duration
                    else: # update duration of previous chord in Measure
                        oPrevious = previousChordInMeasure.getOffsetBySite(m)
                        previousChordInMeasure.quarterLength = o - oPrevious
                    # use source to evaluation roman 
                    try:
                        rn = roman.RomanNumeral(a.src, kCurrent)
                    except:
                        environLocal.printDebug('cannot create RN from: %s' % a.src)
                        rn = note.Note() # create placeholder 
                    rn.addLyric(a.src)
                    m.insert(o, rn)
                    previousChordInMeasure = rn
                    previousChord = rn
            # may need to adjust duration of last chord added
            previousChord.quarterLength = tsCurrent.barDuration.quarterLength - o
            p.append(m)
    p.makeBeams()
    s.insert(0,p)
    return s


def romanTextStringToStreamScore(rtString, inputM21=None):
    '''Convenience routine for geting a score from string
    '''
    # create an empty file obj to get handler from string
    rtf = romanTextModule.RTFile()
    rth = rtf.readstr(rtString) # return handler, processes tokens
    s = romanTextToStreamScore(rth, inputM21=inputM21)
    return s


#-------------------------------------------------------------------------------
class Test(unittest.TestCase):
    
    def runTest(self):
        pass
    
    def testBasicA(self):
        from music21 import romanText
        from music21.romanText import testFiles

        for tf in testFiles.ALL:
            rtf = romanText.RTFile()
            rth = rtf.readstr(tf) # return handler, processes tokens
            s = romanTextToStreamScore(rth)
            #s.show()

        
        s = romanTextStringToStreamScore(testFiles.swv23)
        self.assertEqual(s.metadata.composer, 'Heinrich Schutz')
        # this is defined as a Piece tag, but shows up here as a title, after
        # being set as an alternate title
        self.assertEqual(s.metadata.title, 'Warum toben die Heiden, Psalmen Davids no. 2, SWV 23')
        

        s = romanTextStringToStreamScore(testFiles.riemenschneider001)
        self.assertEqual(s.metadata.composer, 'J. S. Bach')
        self.assertEqual(s.metadata.title, 'Aus meines Herzens Grunde')

        s = romanTextStringToStreamScore(testFiles.monteverdi_3_13)
        self.assertEqual(s.metadata.composer, 'Claudio Monteverdi')

    def testBasicB(self):
        from music21 import romanText
        from music21.romanText import testFiles

        s = romanTextStringToStreamScore(testFiles.riemenschneider001)
        #s.show()

class TestExternal(unittest.TestCase):

    def runTest(self):
        pass
 
    def testExternalA(self):
        from music21 import romanText
        from music21.romanText import testFiles

        for tf in testFiles.ALL:
            rtf = romanText.RTFile()
            rth = rtf.readstr(tf) # return handler, processes tokens
            s = romanTextToStreamScore(rth)
            s.show()

#-------------------------------------------------------------------------------
# define presented order in documentation
_DOC_ORDER = []


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1: # normal conditions
        music21.mainTest(TestExternal)
    elif len(sys.argv) > 1:
        t = Test()
        # arg[1] is test to launch
        if hasattr(t, sys.argv[1]): getattr(t, sys.argv[1])()

#------------------------------------------------------------------------------
# eof