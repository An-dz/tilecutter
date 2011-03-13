#!/usr/bin/python

"""Unit test for project.py"""

import project
import unittest

import wx



class image_path(unittest.TestCase):
    """Test image path validator and image path settings"""
    # By default there are four directions, two seasons, 1 frame and 2 layers
    # Test setting/getting all of these to ensure that this method always sets/returns the correct one
    directions = [0,1,2,3]
    seasons = [0,1]
    frames = [0]
    layers = [0,1]
    knownvalues = (
                   (None,u""),
                   ("string",True),
                   (u"string",True),
                   (True,False),
                   (1,False),
                   (-1,False),
                   ({},False),
                   ([],False),
                  )

    def test_knownvalues_validate(self):
        """Test that known values are validated correctly"""
        for testvalue, expected in self.knownvalues:
            p = project.Project()
            for d in self.directions:
                for s in self.seasons:
                    for f in self.frames:
                        for l in self.layers:
                            result = p.image_path(d,s,f,l, testvalue, validate=True)
                            self.assertEqual(expected, result)

    def test_knownvalues_set(self):
        """Test that known values are set correctly"""
        for testvalue, expected in self.knownvalues:
            p = project.Project()
            for d in self.directions:
                for s in self.seasons:
                    for f in self.frames:
                        for l in self.layers:
                            result = p.image_path(d,s,f,l, testvalue)
                            self.assertEqual(expected, result)

    def test_setvalues(self):
        """Test setting/getting values works"""
        # Try setting a unique value for each view, then reading it back after all have been set
        p = project.Project()
        for d in self.directions:
            for s in self.seasons:
                for f in self.frames:
                    for l in self.layers:
                        testvalue = unicode(d) + unicode(s) + unicode(f) + unicode(l)
                        result = p.image_path(d,s,f,l,testvalue)
                        self.assertEqual(result, True)
        for d in self.directions:
            for s in self.seasons:
                for f in self.frames:
                    for l in self.layers:
                        expected = unicode(d) + unicode(s) + unicode(f) + unicode(l)
                        self.assertEqual(expected, p.image_path(d,s,f,l))

class dat_lump_knownvalues(unittest.TestCase):
    """Test dat_lump validator"""
    knownvalues = (
                   (None,u"Obj=building\nName=test_1\nType=cur\nPassengers=100\nintro_year=1900\nchance=100"),
                   ("string",True),
                   (u"string",True),
                   (True,False),
                   (1,False),
                   (-1,False),
                   ({},False),
                   ([],False),
                  )
    def test_knownvalues_validate(self):
        """Test that known values are validated correctly"""
        for testvalue, expected in self.knownvalues:
            p = project.Project()
            result = p.dat_lump(testvalue, validate=True)
            self.assertEqual(expected, result)

    def test_knownvalues_set(self):
        """Test that known values are set correctly"""
        for testvalue, expected in self.knownvalues:
            p = project.Project()
            result = p.dat_lump(testvalue)
            self.assertEqual(expected, result)

    def test_setvalues(self):
        """Test setting/getting values works"""
        for testvalue, expected in self.knownvalues:
            # Use fresh project instance each time
            p = project.Project()
            # If setting works then the value output should equal the value input
            if p.dat_lump(testvalue) == True:
                self.assertEqual(testvalue, p.dat_lump())

if __name__ == "__main__":
    app = wx.App()
    unittest.main()

