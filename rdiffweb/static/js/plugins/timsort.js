// rdiffweb, A web interface to rdiff-backup repositories
// Copyright (C) 2012-2021 rdiffweb contributors
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

// TimSort implementation ported from Java to JavaScript
// by Patrik Dufresne <patrik@ikus-soft.com>

/**
 * A stable, adaptive, iterative mergesort that requires far fewer than
 * n lg(n) comparisons when running on partially sorted arrays, while
 * offering performance comparable to a traditional mergesort when run
 * on random arrays.  Like all proper mergesorts, this sort is stable and
 * runs O(n log n) time (worst case).  In the worst case, this sort requires
 * temporary storage space for n/2 object references; in the best case,
 * it requires only a small constant amount of space.
 *
 * This implementation was adapted from Tim Peters's list sort for
 * Python, which is described in detail here:
 *
 *   http://svn.python.org/projects/python/trunk/Objects/listsort.txt
 *
 * Tim's C code may be found here:
 *
 *   http://svn.python.org/projects/python/trunk/Objects/listobject.c
 *
 * The underlying techniques are described in this paper (and may have
 * even earlier origins):
 *
 *  "Optimistic Sorting and Information Theoretic Complexity"
 *  Peter McIlroy
 *  SODA (Fourth Annual ACM-SIAM Symposium on Discrete Algorithms),
 *  pp 467-474, Austin, Texas, 25-27 January 1993.
 *
 * While the API to this class consists solely of static methods, it is
 * (privately) instantiable; a TimSort instance holds the state of an ongoing
 * sort, assuming the input array is large enough to warrant the full-blown
 * TimSort. Small arrays are sorted in place, using a binary insertion sort.
 *
 * @author Josh Bloch
 */
function TimSort(a, c) {

    /**
     * The array being sorted.
     */
    this.a = a; 

    /**
     * The comparator for this sort.
     */
    this.c = c;

    /**
     * This controls when we get *into* galloping mode.  It is initialized
     * to MIN_GALLOP.  The mergeLo and mergeHi methods nudge it higher for
     * random data, and lower for highly structured data.
     */
    this.minGallop = 7;

    /**
     * A stack of pending runs yet to be merged.  Run i starts at
     * address base[i] and extends for len[i] elements.  It's always
     * true (so long as the indices are in bounds) that:
     *
     *     runBase[i] + runLen[i] == runBase[i + 1]
     *
     * so we could cut the storage for this, but it's a minor amount,
     * and keeping all the info explicit simplifies the code.
     */
    this.stackSize = 0;  // Number of pending runs on stack
    
    // Allocate temp storage (which may be increased later if necessary)
    var len = this.a.length;
    this.tmp = new Array(len < 2 * TimSort.INITIAL_TMP_STORAGE_LENGTH ?
			len >>> 1 : TimSort.INITIAL_TMP_STORAGE_LENGTH);

    /*
     * Allocate runs-to-be-merged stack (which cannot be expanded).  The
     * stack length requirements are described in listsort.txt.  The C
     * version always uses the same stack length (85), but this was
     * measured to be too expensive when sorting "mid-sized" arrays (e.g.,
     * 100 elements) in Java.  Therefore, we use smaller (but sufficiently
     * large) stack lengths for smaller arrays.  The "magic numbers" in the
     * computation below must be changed if MIN_MERGE is decreased.  See
     * the MIN_MERGE declaration above for more information.
     */
    var stackLen = (len <    120  ?  5 :
                    len <   1542  ? 10 :
                    len < 119151  ? 19 : 40);
    this.runBase = new Array(stackLen);
    this.runLen = new Array(stackLen);
}
    
/**
 * Pushes the specified run onto the pending-run stack.
 *
 * @param runBase index of the first element in the run
 * @param runLen  the number of elements in the run
 */
TimSort.prototype.pushRun = function(runBase, runLen) {
    this.runBase[this.stackSize] = runBase;
    this.runLen[this.stackSize] = runLen;
    this.stackSize++;
}

/**
 * Examines the stack of runs waiting to be merged and merges adjacent runs
 * until the stack invariants are reestablished:
 *
 *     1. runLen[i - 3] > runLen[i - 2] + runLen[i - 1]
 *     2. runLen[i - 2] > runLen[i - 1]
 *
 * This method is called each time a new run is pushed onto the stack,
 * so the invariants are guaranteed to hold for i < stackSize upon
 * entry to the method.
 */
TimSort.prototype.mergeCollapse = function() {
    while (this.stackSize > 1) {
        var n = this.stackSize - 2;
        if (n > 0 && this.runLen[n-1] <= this.runLen[n] + this.runLen[n+1]) {
            if (this.runLen[n - 1] < this.runLen[n + 1])
                n--;
            this.mergeAt(n);
        } else if (this.runLen[n] <= this.runLen[n + 1]) {
            this.mergeAt(n);
        } else {
            break; // Invariant is established
        }
    }
}

/**
 * Merges all runs on the stack until only one remains.  This method is
 * called once, to complete the sort.
 */
TimSort.prototype.mergeForceCollapse = function() {
    while (this.stackSize > 1) {
        var n = this.stackSize - 2;
        if (n > 0 && this.runLen[n - 1] < this.runLen[n + 1])
            n--;
        this.mergeAt(n);
    }
}

/**
 * Merges the two runs at stack indices i and i+1.  Run i must be
 * the penultimate or antepenultimate run on the stack.  In other words,
 * i must be equal to stackSize-2 or stackSize-3.
 *
 * @param i stack index of the first of the two runs to merge
 */
TimSort.prototype.mergeAt = function(i) {
    var base1 = this.runBase[i];
    var len1 = this.runLen[i];
    var base2 = this.runBase[i + 1];
    var len2 = this.runLen[i + 1];

    /*
     * Record the length of the combined runs; if i is the 3rd-last
     * run now, also slide over the last run (which isn't involved
     * in this merge).  The current run (i+1) goes away in any case.
     */
    this.runLen[i] = len1 + len2;
    if (i == this.stackSize - 3) {
        this.runBase[i + 1] = this.runBase[i + 2];
        this.runLen[i + 1] = this.runLen[i + 2];
    }
    this.stackSize--;

    /*
     * Find where the first element of run2 goes in run1. Prior elements
     * in run1 can be ignored (because they're already in place).
     */
    var k = TimSort.gallopRight(this.a[base2], this.a, base1, len1, 0, this.c);
    base1 += k;
    len1 -= k;
    if (len1 == 0)
        return;

    /*
     * Find where the last element of run1 goes in run2. Subsequent elements
     * in run2 can be ignored (because they're already in place).
     */
    len2 = TimSort.gallopLeft(this.a[base1 + len1 - 1], this.a, base2, len2, len2 - 1, this.c);
    if (len2 == 0)
        return;

    // Merge remaining runs, using tmp array with min(len1, len2) elements
    if (len1 <= len2)
        this.mergeLo(base1, len1, base2, len2);
    else
        this.mergeHi(base1, len1, base2, len2);
}

/**
 * Merges two adjacent runs in place, in a stable fashion.  The first
 * element of the first run must be greater than the first element of the
 * second run (a[base1] > a[base2]), and the last element of the first run
 * (a[base1 + len1-1]) must be greater than all elements of the second run.
 *
 * For performance, this method should be called only when len1 <= len2;
 * its twin, mergeHi should be called if len1 >= len2.  (Either method
 * may be called if len1 == len2.)
 *
 * @param base1 index of first element in first run to be merged
 * @param len1  length of first run to be merged (must be > 0)
 * @param base2 index of first element in second run to be merged
 *        (must be aBase + aLen)
 * @param len2  length of second run to be merged (must be > 0)
 */
TimSort.prototype.mergeLo = function(base1, len1, base2, len2) {
    // Copy first run into temp array
    var a = this.a; // For performance
    this.tmp.length = len1;
    TimSort.arraycopy(a, base1, this.tmp, 0, len1);

    var cursor1 = 0;       // Indexes into tmp array
    var cursor2 = base2;   // Indexes int a
    var dest = base1;      // Indexes int a

    // Move first element of second run and deal with degenerate cases
    a[dest++] = a[cursor2++];
    if (--len2 == 0) {
        TimSort.arraycopy(tmp, cursor1, a, dest, len1);
        return;
    }
    if (len1 == 1) {
        TimSort.arraycopy(a, cursor2, a, dest, len2);
        a[dest + len2] = this.tmp[cursor1]; // Last elt of run 1 to end of merge
        return;
    }

    var c = this.c;  // Use local variable for performance
    var minGallop = this.minGallop;    //  "    "       "     "      "
outer:
    while (true) {
        var count1 = 0; // Number of times in a row that first run won
        var count2 = 0; // Number of times in a row that second run won

        /*
         * Do the straightforward thing until (if ever) one run starts
         * winning consistently.
         */
        do {
            if (c(a[cursor2], this.tmp[cursor1]) < 0) {
                a[dest++] = a[cursor2++];
                count2++;
                count1 = 0;
                if (--len2 == 0)
                    break outer;
            } else {
                a[dest++] = this.tmp[cursor1++];
                count1++;
                count2 = 0;
                if (--len1 == 1)
                    break outer;
            }
        } while ((count1 | count2) < minGallop);

        /*
         * One run is winning so consistently that galloping may be a
         * huge win. So try that, and continue galloping until (if ever)
         * neither run appears to be winning consistently anymore.
         */
        do {
            count1 = TimSort.gallopRight(a[cursor2], this.tmp, cursor1, len1, 0, c);
            if (count1 != 0) {
                TimSort.arraycopy(this.tmp, cursor1, a, dest, count1);
                dest += count1;
                cursor1 += count1;
                len1 -= count1;
                if (len1 <= 1) // len1 == 1 || len1 == 0
                    break outer;
            }
            a[dest++] = a[cursor2++];
            if (--len2 == 0)
                break outer;

            count2 = TimSort.gallopLeft(this.tmp[cursor1], a, cursor2, len2, 0, c);
            if (count2 != 0) {
                TimSort.arraycopy(a, cursor2, a, dest, count2);
                dest += count2;
                cursor2 += count2;
                len2 -= count2;
                if (len2 == 0)
                    break outer;
            }
            a[dest++] = this.tmp[cursor1++];
            if (--len1 == 1)
                break outer;
            minGallop--;
        } while (count1 >= TimSort.MIN_GALLOP | count2 >= TimSort.MIN_GALLOP);
        if (minGallop < 0)
            minGallop = 0;
        minGallop += 2;  // Penalize for leaving gallop mode
    }  // End of "outer" loop
    this.minGallop = minGallop < 1 ? 1 : minGallop;  // Write back to field

    if (len1 == 1) {
        TimSort.arraycopy(a, cursor2, a, dest, len2);
        a[dest + len2] = this.tmp[cursor1]; //  Last elt of run 1 to end of merge
    } else if (len1 == 0) {
        throw "IllegalArgumentException Comparison method violates its general contract!";
    } else {
        TimSort.arraycopy(this.tmp, cursor1, a, dest, len1);
    }
}

/**
 * Like mergeLo, except that this method should be called only if
 * len1 >= len2; mergeLo should be called if len1 <= len2.  (Either method
 * may be called if len1 == len2.)
 *
 * @param base1 index of first element in first run to be merged
 * @param len1  length of first run to be merged (must be > 0)
 * @param base2 index of first element in second run to be merged
 *        (must be aBase + aLen)
 * @param len2  length of second run to be merged (must be > 0)
 */
TimSort.prototype.mergeHi = function(base1, len1, base2, len2) {
    // Copy second run into temp array
    var a = this.a; // For performance
    this.tmp.length = len2;
    TimSort.arraycopy(a, base2, this.tmp, 0, len2);

    var cursor1 = base1 + len1 - 1;  // Indexes into a
    var cursor2 = len2 - 1;          // Indexes into tmp array
    var dest = base2 + len2 - 1;     // Indexes into a

    // Move last element of first run and deal with degenerate cases
    a[dest--] = a[cursor1--];
    if (--len1 == 0) {
        TimSort.arraycopy(tmp, 0, a, dest - (len2 - 1), len2);
        return;
    }
    if (len2 == 1) {
        dest -= len1;
        cursor1 -= len1;
        TimSort.arraycopy(a, cursor1 + 1, a, dest + 1, len1);
        a[dest] = this.tmp[cursor2];
        return;
    }

    var c = this.c;  // Use local variable for performance
    var minGallop = this.minGallop;    //  "    "       "     "      "
outer:
    while (true) {
        var count1 = 0; // Number of times in a row that first run won
        var count2 = 0; // Number of times in a row that second run won

        /*
         * Do the straightforward thing until (if ever) one run
         * appears to win consistently.
         */
        do {
            if (c(this.tmp[cursor2], a[cursor1]) < 0) {
                a[dest--] = a[cursor1--];
                count1++;
                count2 = 0;
                if (--len1 == 0)
                    break outer;
            } else {
                a[dest--] = this.tmp[cursor2--];
                count2++;
                count1 = 0;
                if (--len2 == 1)
                    break outer;
            }
        } while ((count1 | count2) < minGallop);

        /*
         * One run is winning so consistently that galloping may be a
         * huge win. So try that, and continue galloping until (if ever)
         * neither run appears to be winning consistently anymore.
         */
        do {
            count1 = len1 - TimSort.gallopRight(this.tmp[cursor2], a, base1, len1, len1 - 1, c);
            if (count1 != 0) {
                dest -= count1;
                cursor1 -= count1;
                len1 -= count1;
                TimSort.arraycopy(a, cursor1 + 1, a, dest + 1, count1);
                if (len1 == 0)
                    break outer;
            }
            a[dest--] = this.tmp[cursor2--];
            if (--len2 == 1)
                break outer;

            count2 = len2 - TimSort.gallopLeft(a[cursor1], this.tmp, 0, len2, len2 - 1, c);
            if (count2 != 0) {
                dest -= count2;
                cursor2 -= count2;
                len2 -= count2;
                TimSort.arraycopy(this.tmp, cursor2 + 1, a, dest + 1, count2);
                if (len2 <= 1)  // len2 == 1 || len2 == 0
                    break outer;
            }
            a[dest--] = a[cursor1--];
            if (--len1 == 0)
                break outer;
            minGallop--;
        } while (count1 >= TimSort.MIN_GALLOP | count2 >= TimSort.MIN_GALLOP);
        if (minGallop < 0)
            minGallop = 0;
        minGallop += 2;  // Penalize for leaving gallop mode
    }  // End of "outer" loop
    this.minGallop = minGallop < 1 ? 1 : minGallop;  // Write back to field

    if (len2 == 1) {
        dest -= len1;
        cursor1 -= len1;
        TimSort.arraycopy(a, cursor1 + 1, a, dest + 1, len1);
        a[dest] = this.tmp[cursor2];  // Move first elt of run2 to front of merge
    } else if (len2 == 0) {
        throw "Comparison method violates its general contract!";
    } else {
        TimSort.arraycopy(this.tmp, 0, a, dest - (len2 - 1), len2);
    }
}

/**
 * This is the minimum sized sequence that will be merged.  Shorter
 * sequences will be lengthened by calling binarySort.  If the entire
 * array is less than this length, no merges will be performed.
 *
 * This constant should be a power of two.  It was 64 in Tim Peter's C
 * implementation, but 32 was empirically determined to work better in
 * this implementation.  In the unlikely event that you set this constant
 * to be a number that's not a power of two, you'll need to change the
 * {@link #minRunLength} computation.
 *
 * If you decrease this constant, you must change the stackLen
 * computation in the TimSort constructor, or you risk an
 * ArrayOutOfBounds exception.  See listsort.txt for a discussion
 * of the minimum stack length required as a function of the length
 * of the array being sorted and the minimum merge sequence length.
 */
TimSort.MIN_MERGE = 32;

/**
 * When we get into galloping mode, we stay there until both runs win less
 * often than MIN_GALLOP consecutive times.
 */
TimSort.MIN_GALLOP = 7;

/**
 * Maximum initial size of tmp array, which is used for merging.  The array
 * can grow to accommodate demand.
 *
 * Unlike Tim's original C version, we do not allocate this much storage
 * when sorting smaller arrays.  This change was required for performance.
 */
TimSort.INITIAL_TMP_STORAGE_LENGTH = 256;

/**
 * Copies an array from the specified source array, beginning at the specified position, to the specified position of the destination array.
 * @param src the source array
 * @param srcPos starting position in the source array
 * @param dest the destination array.
 * @param destPos starting position in the destination data
 * @param length the number of array elements to be copied
 */
TimSort.arraycopy = function(src, srcPos, dest, destPos, length) {
	if(srcPos.length < srcPos
			|| srcPos.length < srcPos+length
			|| dest.length < destPos 
			|| dest.length < destPos + length )
		throw "IndexOutOfBound";
	if(length==0) return;
	if(srcPos < destPos) {
		for (var i = srcPos + length - 1, j = destPos + length - 1; srcPos <= i ; i--, j--) {
			dest[j] = src[i];
		}
	} else {
		for (var i = srcPos, j = destPos; i < length + srcPos; i++, j++) {
			dest[j] = src[i];
		}
		
	}
};

/**
 * Sorts the specified portion of the specified array using a binary
 * insertion sort.  This is the best method for sorting small numbers
 * of elements.  It requires O(n log n) compares, but O(n^2) data
 * movement (worst case).
 *
 * If the initial part of the specified range is already sorted,
 * this method can take advantage of it: the method assumes that the
 * elements from index {@code lo}, inclusive, to {@code start},
 * exclusive are already sorted.
 *
 * @param a the array in which a range is to be sorted
 * @param lo the index of the first element in the range to be sorted
 * @param hi the index after the last element in the range to be sorted
 * @param start the index of the first element in the range that is
 *        not already known to be sorted ({@code lo <= start <= hi})
 * @param c comparator to used for the sort
 */
TimSort.binarySort = function(a, lo, hi, start, c) {
    if (start == lo)
        start++;
    for ( ; start < hi; start++) {
        var pivot = a[start];

        // Set left (and right) to the index where a[start] (pivot) belongs
        var left = lo;
        var right = start;
        /*
         * Invariants:
         *   pivot >= all in [lo, left).
         *   pivot <  all in [right, start).
         */
        while (left < right) {
            var mid = (left + right) >>> 1;
            if (c(pivot, a[mid]) < 0)
                right = mid;
            else
                left = mid + 1;
        }

        /*
         * The invariants still hold: pivot >= all in [lo, left) and
         * pivot < all in [left, start), so pivot belongs at left.  Note
         * that if there are elements equal to pivot, left points to the
         * first slot after them -- that's why this sort is stable.
         * Slide elements over to make room for pivot.
         */
        var n = start - left;  // The number of elements to move
        // Switch is just an optimization for arraycopy in default case
        switch (n) {
            case 2:  a[left + 2] = a[left + 1];
            case 1:  a[left + 1] = a[left];
                     break;
            default: TimSort.arraycopy(a, left, a, left + 1, n);
        }
        a[left] = pivot;
    }
}

/**
 * Returns the length of the run beginning at the specified position in
 * the specified array and reverses the run if it is descending (ensuring
 * that the run will always be ascending when the method returns).
 *
 * A run is the longest ascending sequence with:
 *
 *    a[lo] <= a[lo + 1] <= a[lo + 2] <= ...
 *
 * or the longest descending sequence with:
 *
 *    a[lo] >  a[lo + 1] >  a[lo + 2] >  ...
 *
 * For its intended use in a stable mergesort, the strictness of the
 * definition of "descending" is needed so that the call can safely
 * reverse a descending sequence without violating stability.
 *
 * @param a the array in which a run is to be counted and possibly reversed
 * @param lo index of the first element in the run
 * @param hi index after the last element that may be contained in the run.
          It is required that {@code lo < hi}.
 * @param c the comparator to used for the sort
 * @return  the length of the run beginning at the specified position in
 *          the specified array
 */
TimSort.countRunAndMakeAscending = function(a, lo, hi, c) {
    var runHi = lo + 1;
    if (runHi == hi)
        return 1;

    // Find end of run, and reverse range if descending
    if (c(a[runHi++], a[lo]) < 0) { // Descending
        while (runHi < hi && c(a[runHi], a[runHi - 1]) < 0)
            runHi++;
        TimSort.reverseRange(a, lo, runHi);
    } else {                              // Ascending
        while (runHi < hi && c(a[runHi], a[runHi - 1]) >= 0)
            runHi++;
    }

    return runHi - lo;
}

/**
 * Locates the position at which to insert the specified key into the
 * specified sorted range; if the range contains an element equal to key,
 * returns the index of the leftmost equal element.
 *
 * @param key the key whose insertion point to search for
 * @param a the array in which to search
 * @param base the index of the first element in the range
 * @param len the length of the range; must be > 0
 * @param hint the index at which to begin the search, 0 <= hint < n.
 *     The closer hint is to the result, the faster this method will run.
 * @param c the comparator used to order the range, and to search
 * @return the int k,  0 <= k <= n such that a[b + k - 1] < key <= a[b + k],
 *    pretending that a[b - 1] is minus infinity and a[b + n] is infinity.
 *    In other words, key belongs at index b + k; or in other words,
 *    the first k elements of a should precede key, and the last n - k
 *    should follow it.
 */
TimSort.gallopLeft = function(key, a, base, len, hint, c) {
    var lastOfs = 0;
    var ofs = 1;
    if (c(key, a[base + hint]) > 0) {
        // Gallop right until a[base+hint+lastOfs] < key <= a[base+hint+ofs]
        var maxOfs = len - hint;
        while (ofs < maxOfs && c(key, a[base + hint + ofs]) > 0) {
            lastOfs = ofs;
            ofs = (ofs << 1) + 1;
            if (ofs <= 0)   // int overflow
                ofs = maxOfs;
        }
        if (ofs > maxOfs)
            ofs = maxOfs;

        // Make offsets relative to base
        lastOfs += hint;
        ofs += hint;
    } else { // key <= a[base + hint]
        // Gallop left until a[base+hint-ofs] < key <= a[base+hint-lastOfs]
        var maxOfs = hint + 1;
        while (ofs < maxOfs && c(key, a[base + hint - ofs]) <= 0) {
            lastOfs = ofs;
            ofs = (ofs << 1) + 1;
            if (ofs <= 0)   // int overflow
                ofs = maxOfs;
        }
        if (ofs > maxOfs)
            ofs = maxOfs;

        // Make offsets relative to base
        var tmp = lastOfs;
        lastOfs = hint - ofs;
        ofs = hint - tmp;
    }

    /*
     * Now a[base+lastOfs] < key <= a[base+ofs], so key belongs somewhere
     * to the right of lastOfs but no farther right than ofs.  Do a binary
     * search, with invariant a[base + lastOfs - 1] < key <= a[base + ofs].
     */
    lastOfs++;
    while (lastOfs < ofs) {
        var m = lastOfs + ((ofs - lastOfs) >>> 1);

        if (c(key, a[base + m]) > 0)
            lastOfs = m + 1;  // a[base + m] < key
        else
            ofs = m;          // key <= a[base + m]
    }
    return ofs;
}

/**
 * Like gallopLeft, except that if the range contains an element equal to
 * key, gallopRight returns the index after the rightmost equal element.
 *
 * @param key the key whose insertion point to search for
 * @param a the array in which to search
 * @param base the index of the first element in the range
 * @param len the length of the range; must be > 0
 * @param hint the index at which to begin the search, 0 <= hint < n.
 *     The closer hint is to the result, the faster this method will run.
 * @param c the comparator used to order the range, and to search
 * @return the int k,  0 <= k <= n such that a[b + k - 1] <= key < a[b + k]
 */
TimSort.gallopRight = function(key, a, base, len, hint, c) {

    var ofs = 1;
    var lastOfs = 0;
    if (c(key, a[base + hint]) < 0) {
        // Gallop left until a[b+hint - ofs] <= key < a[b+hint - lastOfs]
        var maxOfs = hint + 1;
        while (ofs < maxOfs && c(key, a[base + hint - ofs]) < 0) {
            lastOfs = ofs;
            ofs = (ofs << 1) + 1;
            if (ofs <= 0)   // int overflow
                ofs = maxOfs;
        }
        if (ofs > maxOfs)
            ofs = maxOfs;

        // Make offsets relative to b
        var tmp = lastOfs;
        lastOfs = hint - ofs;
        ofs = hint - tmp;
    } else { // a[b + hint] <= key
        // Gallop right until a[b+hint + lastOfs] <= key < a[b+hint + ofs]
        var maxOfs = len - hint;
        while (ofs < maxOfs && c(key, a[base + hint + ofs]) >= 0) {
            lastOfs = ofs;
            ofs = (ofs << 1) + 1;
            if (ofs <= 0)   // int overflow
                ofs = maxOfs;
        }
        if (ofs > maxOfs)
            ofs = maxOfs;

        // Make offsets relative to b
        lastOfs += hint;
        ofs += hint;
    }

    /*
     * Now a[b + lastOfs] <= key < a[b + ofs], so key belongs somewhere to
     * the right of lastOfs but no farther right than ofs.  Do a binary
     * search, with invariant a[b + lastOfs - 1] <= key < a[b + ofs].
     */
    lastOfs++;
    while (lastOfs < ofs) {
        var m = lastOfs + ((ofs - lastOfs) >>> 1);

        if (c(key, a[base + m]) < 0)
            ofs = m;          // key < a[b + m]
        else
            lastOfs = m + 1;  // a[b + m] <= key
    }
    return ofs;
}

/**
 * Returns the minimum acceptable run length for an array of the specified
 * length. Natural runs shorter than this will be extended with
 * {@link #binarySort}.
 *
 * Roughly speaking, the computation is:
 *
 *  If n < MIN_MERGE, return n (it's too small to bother with fancy stuff).
 *  Else if n is an exact power of 2, return MIN_MERGE/2.
 *  Else return an int k, MIN_MERGE/2 <= k <= MIN_MERGE, such that n/k
 *   is close to, but strictly less than, an exact power of 2.
 *
 * For the rationale, see listsort.txt.
 *
 * @param n the length of the array to be sorted
 * @return the length of the minimum run to be merged
 */
TimSort.minRunLength = function(n) {
    var r = 0;      // Becomes 1 if any 1 bits are shifted off
    while (n >= TimSort.MIN_MERGE) {
        r |= (n & 1);
        n >>= 1;
    }
    return n + r;
}

/**
 * Checks that fromIndex and toIndex are in range, and throws an
 * appropriate exception if they aren't.
 *
 * @param arrayLen the length of the array
 * @param fromIndex the index of the first element of the range
 * @param toIndex the index after the last element of the range
 * @throws IllegalArgumentException if fromIndex > toIndex
 * @throws ArrayIndexOutOfBoundsException if fromIndex < 0
 *         or toIndex > arrayLen
 */
TimSort.rangeCheck = function(arrayLen, fromIndex, toIndex) {
    if (fromIndex > toIndex)
        throw "IllegalArgumentException fromIndex" + fromIndex + "> toIndex" + toIndex;
	if (fromIndex < 0)
	    throw "ArrayIndexOutOfBoundsException " + fromIndex;
	if (toIndex > arrayLen)
	    throw "ArrayIndexOutOfBoundsException " + toIndex;
}

/**
 * Reverse the specified range of the specified array.
 *
 * @param a the array in which a range is to be reversed
 * @param lo the index of the first element in the range to be reversed
 * @param hi the index after the last element in the range to be reversed
 */
TimSort.reverseRange = function(a, lo, hi) {
    hi--;
    while (lo < hi) {
        var t = a[lo];
        a[lo++] = a[hi];
        a[hi--] = t;
    }
}

TimSort.sort = function(a, c) {
	if(!c){
		c = function(obj1, obj2){
    		return (obj1 < obj2 ? -1 : (obj1 > obj2 ? 1 : 0 ));
    	}
	}
	TimSort.sort1(a, 0, a.length, c);
	return a;
}

TimSort.sort1 = function(a, lo, hi, c) {
    //if (c == null) {
    //    Arrays.sort(a, lo, hi);
    //    return;
    //}

    TimSort.rangeCheck(a.length, lo, hi);
    var nRemaining  = hi - lo;
    if (nRemaining < 2)
        return;  // Arrays of size 0 and 1 are always sorted

    // If array is small, do a "mini-TimSort" with no merges
    if (nRemaining < TimSort.MIN_MERGE) {
        var initRunLen = TimSort.countRunAndMakeAscending(a, lo, hi, c);
        TimSort.binarySort(a, lo, hi, lo + initRunLen, c);
        return;
    }

    /**
     * March over the array once, left to right, finding natural runs,
     * extending short natural runs to minRun elements, and merging runs
     * to maintain stack invariant.
     */
    var ts = new TimSort(a, c);
    var minRun = TimSort.minRunLength(nRemaining);
    do {
        // Identify next run
        var runLen = TimSort.countRunAndMakeAscending(a, lo, hi, c);

        // If run is short, extend to min(minRun, nRemaining)
        if (runLen < minRun) {
            var force = nRemaining <= minRun ? nRemaining : minRun;
            TimSort.binarySort(a, lo, lo + force, lo + runLen, c);
            runLen = force;
        }

        // Push run onto pending-run stack, and maybe merge
        ts.pushRun(lo, runLen);
        ts.mergeCollapse();

        // Advance to find next run
        lo += runLen;
        nRemaining -= runLen;
    } while (nRemaining != 0);

    // Merge all remaining runs to complete sort
    ts.mergeForceCollapse();
}

var Comparators = function(){
	
}
/**
 * Comparator used to sort the date using the natural order of the data type.
 * @param a
 * @param b
 * @throw Exception if the datatype doesn't matches.
 */
Comparators.naturalComparator = function(a, b){
	if(typeof a != typeof b) throw "Datatype can't be compare: "+ a + " ~ " + b;
    if(a > b) return 1;
    if(a < b) return -1;
    return 0;
}
/**
 * Comparator used to sort the string using the natural order of the data type.
 * @param a
 * @param b
 * @throw Exception if the datatype doesn't matches.
 */
Comparators.naturalStrComparator = function(a, b){
	a = String(a); b = String(b);
	if(a > b) return 1;
    if(a < b) return -1;
    return 0;
}
/**
 * Comparator used to sort the integer using the natural order of the data type.
 * @param a
 * @param b
 * @throw Exception if the datatype doesn't matches.
 */
Comparators.naturalIntComparator = function(a, b){
	a = parseInt(a); b = parseInt(b);
	if(a > b) return 1;
    if(a < b) return -1;
    return 0;
}