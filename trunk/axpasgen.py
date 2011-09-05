##########
# axpasgen generates passwords given a base password, multiple seed values, and a target identifier (for example, a website name)
##########

### usage: axpasgen.py [identifier] {password} {configfile}

import sys

if len(sys.argv) < 2:
	print('usage: axpasgen.py [identifier] {password} {configfile}')
	sys.exit(0)

import hashlib
import random
import string
import getpass
import os
import math

# first, read our seed values; if not present, then generate

identifier = sys.argv[1]
password = 0
inputFile = 'axpasgen.cfg'

if len(sys.argv) > 2:
	password = sys.argv[2]
else:
	password = getpass.getpass()

if len(sys.argv) > 3:
	inputFile = sys.argv[3]

fin = 0

seedIterations = 1000
seedRandom = ''
possibleCharacters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$&[{}(=*)+]!#\|\';,.:<>"-_~';
doFloor = True # whether to floor when converting bases; for compatability
generateValues = False

try:
	fin = open(inputFile, 'r')
	
	seedIterations = int(fin.readline()[:-1])
	seedRandom = fin.readline()[:-1]
	
	try:
		seedRandom = seedRandom.decode("hex")
	except:
		print("Error while hex-decoding seedRandom; assuming old format...")
	
	possibleCharacters = fin.readline()[:-1]
	
	floorLine = fin.readline()
	if len(floorLine) == 0:
		doFloor = False
	else:
		doFloor = bool(floorLine[:-1]);

	fin.close()
except IOError:
	print("Error while opening or reading from " + inputFile + ", generating new values")
	generateValues = True
except:
	print("Error while processing seed values, generating new values")
	generateValues = True

if generateValues:
	seedIterations = random.randint(1000, 3000)
	seedRandom = os.urandom(1024)
	
	print("Writing generated seed values to " + inputFile + "...")
	
	fout = open(inputFile, 'w')
	fout.write(str(seedIterations) + "\n")
	fout.write(seedRandom.encode("hex") + "\n")
	fout.write(possibleCharacters + "\n")
	fout.write(str(doFloor) + "\n")

print("Using iterations=" + str(seedIterations) + ", random_length=" + str(len(seedRandom)) + ", and floor=" + str(doFloor) + "...")

# initialize by hashing the password with the random seed
mInit = hashlib.sha512()
mInit.update(password)
mInit.update(seedRandom)
sInit = mInit.digest()

# continue by hashing the result with the identifier
mNext = hashlib.sha512()
mNext.update(sInit)
mNext.update(identifier)
sNext = mNext.digest()

# hash again with the random seed
mLast = hashlib.sha512()
mLast.update(sNext)
mLast.update(seedRandom)
sIter = mLast.digest()

# now hash for seedIterations times with sha512
for x in range(seedIterations):
	m = hashlib.sha512()
	m.update(sIter)
	sIter = m.digest()

# almost done, hash with md5 so that we have something short to print
mFinal = hashlib.md5()
mFinal.update(sIter)
sFinal = mFinal.digest()

print("hexresult: " + mFinal.hexdigest())

# convert base by adding up and then dividing (use decimal class)
from decimal import *

# precision of 40 is more than enough (stores 256^16 nicely)
setcontext(Context(prec=40))

convertFrom = Decimal(256)
convertTotal = Decimal(0)
convertTo = len(possibleCharacters)

# first add up
for x in range(len(sFinal)):
	c = Decimal(ord(sFinal[x]))
	convertTotal += c * (convertFrom ** x)

# now divide down, forming string as we go along
sReadable = ""

while convertTotal >= 1:
	x = convertTotal % convertTo
	sReadable += possibleCharacters[int(x)]

	if doFloor:
		convertTotal = math.floor(convertTotal / convertTo)
	else:
		convertTotal /= convertTo

print("result: " + sReadable)
