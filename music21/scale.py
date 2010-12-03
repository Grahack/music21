#!/usr/bin/python
#-------------------------------------------------------------------------------
# Name:         scale.py
# Purpose:      music21 classes for representing scales
#
# Authors:      Michael Scott Cuthbert
#               Christopher Ariza
#
# Copyright:    (c) 2009-2010 The music21 Project
# License:      LGPL
#-------------------------------------------------------------------------------

'''Objects for defining scales. 
'''

import copy
import unittest, doctest

import music21
from music21 import common
from music21 import pitch
from music21 import interval
from music21 import intervalNetwork



#-------------------------------------------------------------------------------
class ScaleException(Exception):
    pass

class Scale(music21.Music21Object):
    '''
    Generic base class for all scales.
    '''
    def __init__(self):
        self.directionSensitive = False # can be true or false
        self.type = 'Scale' # could be mode, could be other indicator

    def _getName(self):
        '''Return or construct the name of this scale
        '''
        return self.type
        
    name = property(_getName, 
        doc = '''Return or construct the name of this scale.

        ''')

# instead of classes, these can be attributes on the scale object
# class DirectionlessScale(Scale):
#     '''A DirectionlessScale is the same ascending and descending.
#     For instance, the major scale.  
# 
#     A DirectionSensitiveScale has
#     two different forms.  For instance, the natural-minor scale.
#     
#     One could imagine more complex scales that have different forms
#     depending on what scale degree you've just landed on.  Some
#     Ragas might be expressible in that way.'''
#     
#     def ascending(self):
#         return self.pitchList
#     
#     def descending(self):
#         tempScale = copy(self.pitchList)
#         return tempScale.reverse()
#         ## we perform the reverse on a copy of the pitchList so that
#         ## in case we are multithreaded later in life, we do not have
#         ## a race condition where someone might get self.pitchList as
#         ## reversed
# 
# class DirectionSensitiveScale(Scale):
#     pass


#-------------------------------------------------------------------------------
class AbstractScale(Scale):
    '''An abstract scale is specific scale formation, but does not have a defined pitch collection or reference. For example, all Major scales can be represented by an AbstractScale; a ConcreteScale, however, is a specific Major Scale, such as G Major. 
    '''
    isConcrete = False
    def __init__(self):
        Scale.__init__(self)
        # store interval network within abstract scale
        self.net = None

    def reverse(self):
        '''Reverse all intervals in this scale.
        '''
        pass


    def getRealization(self, pitchObj, stepOfPitch, 
                        minPitch=None, maxPitch=None):
        '''Realize the abstract scale as a list of pitch objects, given a pitch object, the step of that pitch object, and a min and max pitch.
        '''
        if self.net is None:
            raise ScaleException('no netowrk is defined.')

        return self.net.realizePitch(pitchObj, stepOfPitch, minPitch=minPitch, maxPitch=maxPitch)



class AbstractDiatonicScale(AbstractScale):
    def __init__(self, tonic = pitch.Pitch()):
        AbstractScale.__init__(self)
        self.type = 'Abstract Diatonic'
        self.tonicStep = None # step of tonic
        self.dominantStep = None # step of domiannt

    def buildNetwork(self, mode=None):
        '''
        Given sub-class dependent parameters, build and assign the IntervalNetwork.
        '''

        # most diatonic scales will start with this collection
        srcList = ['M2', 'M2', 'm2', 'M2', 'M2', 'M2', 'm2']

        if mode in ['dorian']:
            intervalList = srcList[1:] + srcList[:1] # d to d
            self.tonicStep = 1
            self.dominantStep = 5

        elif mode in ['phrygian']:
            intervalList = srcList[2:] + srcList[:2] # e to e
            self.tonicStep = 1
            self.dominantStep = 5

        elif mode in ['lydian']:
            intervalList = srcList[3:] + srcList[:3] # f to f
            self.tonicStep = 1
            self.dominantStep = 5

        elif mode in ['mixolydian']:
            intervalList = srcList[4:] + srcList[:4] # g to g
            self.tonicStep = 1
            self.dominantStep = 5

        elif mode in ['hypodorian']:
            intervalList = srcList[5:] + srcList[:5] # a to a
            self.tonicStep = 4
            self.dominantStep = 6

        elif mode in ['hypophrygian']:
            intervalList = srcList[6:] + srcList[:6] # b to b
            self.tonicStep = 4
            self.dominantStep = 7

        elif mode in ['hypolydian']: # c to c
            intervalList = srcList
            self.tonicStep = 4
            self.dominantStep = 6

        elif mode in ['hypomixolydian']:
            intervalList = srcList[1:] + srcList[:1] # d to d
            self.tonicStep = 4
            self.dominantStep = 7


        elif mode in ['aeolian', 'minor']:
            intervalList = srcList[5:] + srcList[:5] # a to A
            self.tonicStep = 1
            self.dominantStep = 5

        elif mode in [None, 'major', 'ionian']: # c to C
            intervalList = srcList
            self.tonicStep = 1
            self.dominantStep = 5

        elif mode in ['locrian']:
            intervalList = srcList[6:] + srcList[:6] # b to B
            self.tonicStep = 1
            self.dominantStep = 5

        elif mode in ['hypoaeolian']:
            intervalList = srcList[2:] + srcList[:2] # e to e
            self.tonicStep = 4
            self.dominantStep = 6

        elif mode in ['hupomixolydian']:
            intervalList = srcList[3:] + srcList[:3] # f to f
            self.tonicStep = 4
            self.dominantStep = 7

        self.net = intervalNetwork.IntervalNetwork(intervalList)
        # might also set weights for tonic and dominant here





#-------------------------------------------------------------------------------
class ConcreteScale(Scale):
    '''A concrete scale is specific scale formation with a defined collection that may or may not be bound by specific range. For example, a specific Major Scale, such as G Major, from G2 to G4.

    This is class is not generally used directly but a base class for all concrete scales.
    '''

    isConcrete = True

    def __init__(self, tonic=None):
        Scale.__init__(self)

        self.type = 'Concrete'

        # store an instance of an abstract scale
        # subclasses might use multiple abstract scales?
        self._abstract = None

        # determine wether this is a limited range
        self.boundRange = False

        # here, tonic is a pitch

        if tonic is None:
            self._tonic = pitch.Pitch()
        elif common.isStr(tonic):
            self._tonic = pitch.Pitch(tonic)
        elif hasattr(tonic, 'classes') and 'GeneralNote' in tonic.classes:
            self._tonic = tonic.pitch
        else: # assume this is a pitch object
            self._tonic = tonic


    def _getName(self):
        '''Return or construct the name of this scale
        '''
        return " ".join([self._tonic.name, self.type]) 

    name = property(_getName, 
        doc = '''Return or construct the name of this scale.

        >>> from music21 import *
        >>> sc = scale.DiatonicScale()
        >>> sc.name
        'C Concrete'
        ''')



    def getTonic(self):
        '''Return the tonic. 

        This method may be overridden by subclasses that have alternative definitions of tonic. 

        >>> from music21 import *
        >>> sc = scale.ConcreteScale('e-')
        >>> sc.getTonic()
        E-
        '''
        return self._tonic



    def getAbstract(self):
        '''Return the underlying abstract scale
        '''
        # TODO: make abtract a property?
        # copy before returning?
        return self._abstract

    def transpose(self, value, inPlace=False):
        '''Transpose this Scale by the given interval
        '''
        # note: it does not makes sense to transpose an abstract scale;
        # thus, only concrete scales can be transposed. 
        pass

    def getPitchList(self, minPitch=None, maxPitch=None, direction=None):
        '''Return a list of Pitch objects, using a deepcopy of a cached version if available. 
        '''
        # get from interval network of abstract scale
        if self._abstract is not None:
            # TODO: get and store in cache; return a copy
            # or generate from network stored in abstract
            pitchObj = self._tonic
            stepOfPitch = self._abstract.tonicStep

            # this creates new pitche son each call
            return self._abstract.getRealization(pitchObj, stepOfPitch, 
                        minPitch=minPitch, maxPitch=maxPitch)

            #return self._abstract.net.realizePitch(self._tonic, 1)
        else:
            return []
        #raise ScaleException("Cannot generate a scale from a DiatonicScale class")

    pitchList = property(getPitchList, 
        doc ='''Get a default pitch list from this scale.
        ''')

    def pitchFromScaleDegree(self, degree):        
        '''Return a pitch for a scale degree. 

        Subclass may override if there are different modulo degree sizes
        Or, get from intervalNetwork. 
        '''
        # get from network
        if 0 < degree <= 7: 
            return self.getPitchList()[degree - 1]
        else: 
            raise("Scale degree is out of bounds: must be between 1 and 7.")


#     def ascending(self):
#         '''Return ascending scale form.
#         '''
#         # get from pitch cache
#         return self.getPitchList()
#     
#     def descending(self):
#         '''Return descending scale form.
#         '''
#         # get from pitch cache
#         tempScale = copy(self.getPitchList())
#         tempScale.reverse()
#         return tempScale





class DiatonicScale(ConcreteScale):
    '''A concrete diatonic scale. Assumes that all such scales have 
    '''

    isConcrete = True

    def __init__(self, tonic=None):
        ConcreteScale.__init__(self, tonic=tonic)
        self._abstract = AbstractDiatonicScale()

    def getTonic(self):
        '''Return the dominant. 

        >>> from music21 import *
        >>> sc = scale.MajorScale('e-')
        >>> sc.getDominant()
        B-4
        >>> sc = scale.MajorScale('F#')
        >>> sc.getDominant()
        C#5
        '''
        # NOTE: override method on ConcreteScale that simply returns _tonic
        return self.pitchFromScaleDegree(self._abstract.tonicStep)

    def getDominant(self):
        '''Return the dominant. 

        >>> from music21 import *
        >>> sc = scale.MajorScale('e-')
        >>> sc.getDominant()
        B-4
        >>> sc = scale.MajorScale('F#')
        >>> sc.getDominant()
        C#5
        '''
        return self.pitchFromScaleDegree(self._abstract.dominantStep)
    

    def getLeadingTone(self):
        '''Return the leading tone. 

        >>> from music21 import *
        >>> sc = scale.MinorScale('c')
        >>> sc.pitchFromScaleDegree(7)
        B-4
        >>> sc.getLeadingTone()
        B4
        >>> sc.getDominant()
        G4

        '''
        # NOTE: must be adjust for modes that do not have a proper leading tone
        interval1to7 = interval.notesToInterval(self._tonic, 
                        self.pitchFromScaleDegree(7))
        if interval1to7.name != 'M7':
            # if not a major seventh from the tonic, get a pitch a M7 above
            return interval.transposePitch(self.pitchFromScaleDegree(1), "M7")
        else:
            return self.pitchFromScaleDegree(7)





class MajorScale(DiatonicScale):
    '''A Major Scale

    >>> sc = MajorScale(pitch.Pitch('d'))
    >>> sc.pitchFromScaleDegree(7).name
    'C#'
    '''
    
    def __init__(self, tonic=None):

        DiatonicScale.__init__(self, tonic=tonic)
        self.type = "major"
        # build the network for the appropriate scale
        self._abstract.buildNetwork(self.type)


    def getRelativeMinor(self):
        '''Return a relative minor scale based on this concrete major scale.

        >>> sc1 = MajorScale(pitch.Pitch('a'))
        >>> sc1.pitchList
        [A, B4, C#5, D5, E5, F#5, G#5, A5]
        >>> sc2 = sc1.getRelativeMinor()
        >>> sc2.pitchList
        [F#5, G#5, A5, B5, C#6, D6, E6, F#6]
        '''
        return MinorScale(self.pitchFromScaleDegree(6))

    def getParallelMinor(self):
        '''Return a parallel minor scale based on this concrete major scale.

        >>> sc1 = MajorScale(pitch.Pitch('a'))
        >>> sc1.pitchList
        [A, B4, C#5, D5, E5, F#5, G#5, A5]
        >>> sc2 = sc1.getParallelMinor()
        >>> sc2.pitchList
        [A, B4, C5, D5, E5, F5, G5, A5]
        '''
        return MinorScale(self._tonic)




class MinorScale(DiatonicScale):
    '''A natural minor scale, or the Aeolian mode.

    >>> sc = MinorScale(pitch.Pitch('g'))
    >>> sc.pitchList
    [G, A4, B-4, C5, D5, E-5, F5, G5]
    '''
    def __init__(self, tonic=None):
        DiatonicScale.__init__(self, tonic=tonic)
        self.type = "minor"
        self._abstract.buildNetwork(self.type)

    def getRelativeMajor(self):
        '''Return a concrete relative major scale

        >>> sc1 = MinorScale(pitch.Pitch('g'))
        >>> sc1.pitchList
        [G, A4, B-4, C5, D5, E-5, F5, G5]
        >>> sc2 = sc1.getRelativeMajor()
        >>> sc2.pitchList
        [B-4, C5, D5, E-5, F5, G5, A5, B-5]
        '''
        return MajorScale(self.pitchFromScaleDegree(3))

    def getParallelMajor(self):
        '''Return a concrete relative major scale

        >>> sc1 = MinorScale(pitch.Pitch('g'))
        >>> sc1.pitchList
        [G, A4, B-4, C5, D5, E-5, F5, G5]
        >>> sc2 = sc1.getParallelMajor()
        >>> sc2.pitchList
        [G, A4, B4, C5, D5, E5, F#5, G5]
        '''
        return MajorScale(self._tonic)



class DorianScale(DiatonicScale):
    '''A natural minor scale, or the Aeolian mode.

    >>> sc = DorianScale(pitch.Pitch('d'))
    >>> sc.pitchList
    [D, E4, F4, G4, A4, B4, C5, D5]
    '''
    def __init__(self, tonic=None):
        DiatonicScale.__init__(self, tonic=tonic)
        self.type = "dorian"
        self._abstract.buildNetwork(self.type)


class PhrygianScale(DiatonicScale):
    '''A natural minor scale, or the Aeolian mode.

    >>> sc = PhrygianScale(pitch.Pitch('e'))
    >>> sc.pitchList
    [E, F4, G4, A4, B4, C5, D5, E5]
    '''
    def __init__(self, tonic=None):
        DiatonicScale.__init__(self, tonic=tonic)
        self.type = "phrygian"
        self._abstract.buildNetwork(self.type)



#     def getConcreteHarmonicMinorScale(self):
#         scale = self.pitchList[:]
#         scale[6] = self.getLeadingTone()
#         scale.append(interval.transposePitch(self._tonic, "P8"))
#         return scale

#     def getAbstractHarmonicMinorScale(self):
#         concrete = self.getConcreteHarmonicMinorScale()
#         abstract = copy.deepcopy(concrete)
#         for pitch1 in abstract:
#             pitch1.octave = 0 #octave 0 means "octaveless"
#         return abstract
# 




# melodic minor will be implemented in a different way
#     def getConcreteMelodicMinorScale(self):
#         scale = self.getConcreteHarmonicMinorScale()
#         scale[5] = interval.transposePitch(self.pitchFromScaleDegree(6), "A1")
#         for n in range(0, 7):
#             scale.append(self.pitchFromScaleDegree(7-n))
#         return scale
# 
#     def getAbstractMelodicMinorScale(self):
#         concrete = self.getConcreteMelodicMinorScale()
#         abstract = copy.deepcopy(concrete)
#         for pitch1 in abstract:
#             pitch1.octave = 0 #octave 0 means "octaveless"
#         return abstract






#-------------------------------------------------------------------------------
class Test(unittest.TestCase):
    
    def runTest(self):
        pass


    def testBasicLegacy(self):
        from music21 import note

        n1 = note.Note()
        
        CMajor = MajorScale(n1)
        
        assert CMajor.name == "C major"
        assert CMajor.getPitchList()[6].step == "B"
        
#         CScale = CMajor.getConcreteMajorScale()
#         assert CScale[7].step == "C"
#         assert CScale[7].octave == 5
#         
#         CScale2 = CMajor.getAbstractMajorScale()
#         
#         for note1 in CScale2:
#             assert note1.octave == 0
#             #assert note1.duration.type == ""
#         assert [note1.name for note1 in CScale] == ["C", "D", "E", "F", "G", "A", "B", "C"]
        
        seventh = CMajor.pitchFromScaleDegree(7)
        assert seventh.step == "B"
        
        dom = CMajor.getDominant()
        assert dom.step == "G"
        
        n2 = note.Note()
        n2.step = "A"
        
        aMinor = CMajor.getRelativeMinor()
        assert aMinor.name == "A minor", "Got a different name: " + aMinor.name
        
        notes = [note1.name for note1 in aMinor.getPitchList()]
        self.assertEqual(notes, ["A", "B", "C", "D", "E", "F", "G", 'A'])
        
        n3 = note.Note()
        n3.name = "B-"
        n3.octave = 5
        
        bFlatMinor = MinorScale(n3)
        assert bFlatMinor.name == "B- minor", "Got a different name: " + bFlatMinor.name
        notes2 = [note1.name for note1 in bFlatMinor.getPitchList()]
        self.assertEqual(notes2, ["B-", "C", "D-", "E-", "F", "G-", "A-", 'B-'])
        assert bFlatMinor.getPitchList()[0] == n3
        assert bFlatMinor.getPitchList()[6].octave == 6
        
#         harmonic = bFlatMinor.getConcreteHarmonicMinorScale()
#         niceHarmonic = [note1.name for note1 in harmonic]
#         assert niceHarmonic == ["B-", "C", "D-", "E-", "F", "G-", "A", "B-"]
#         
#         harmonic2 = bFlatMinor.getAbstractHarmonicMinorScale()
#         assert [note1.name for note1 in harmonic2] == niceHarmonic
#         for note1 in harmonic2:
#             assert note1.octave == 0
#             #assert note1.duration.type == ""
        
#         melodic = bFlatMinor.getConcreteMelodicMinorScale()
#         niceMelodic = [note1.name for note1 in melodic]
#         assert niceMelodic == ["B-", "C", "D-", "E-", "F", "G", "A", "B-", "A-", "G-", \
#                                "F", "E-", "D-", "C", "B-"]
        
#         melodic2 = bFlatMinor.getAbstractMelodicMinorScale()
#         assert [note1.name for note1 in melodic2] == niceMelodic
#         for note1 in melodic2:
#             assert note1.octave == 0
            #assert note1.duration.type == ""
        
        cNote = bFlatMinor.pitchFromScaleDegree(2)
        assert cNote.name == "C"
        fNote = bFlatMinor.getDominant()
        assert fNote.name == "F"
        
        bFlatMajor = bFlatMinor.getParallelMajor()
        assert bFlatMajor.name == "B- major"
#         scale = [note1.name for note1 in bFlatMajor.getConcreteMajorScale()]
#         assert scale == ["B-", "C", "D", "E-", "F", "G", "A", "B-"]
        
        dFlatMajor = bFlatMinor.getRelativeMajor()
        assert dFlatMajor.name == "D- major"
        assert dFlatMajor.getTonic().name == "D-"
        assert dFlatMajor.getDominant().name == "A-"



#-------------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1: # normal conditions
        music21.mainTest(Test)
    elif len(sys.argv) > 1:
        t = Test()



#------------------------------------------------------------------------------
# eof

