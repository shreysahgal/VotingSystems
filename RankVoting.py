import os, csv
from itertools import combinations

#####################################################
############# Preference Schedule Class #############
#####################################################

class PreferenceSchedule:
    def __init__(self, file):
        self.file = file
        self.candidates, self.pref_sched = self.parse_file()
    
    # pretty print preference schedules as they are meant to be formatted
    def __str__(self):
        counts_dict = dict()
        # first count how many times each combination appears
        for i in self.pref_sched:
            i = ",".join(i) # can't hash lists so have to join them and split them later
            if i in counts_dict:
                counts_dict[i] += 1
            else:
                counts_dict[i] = 1
        # counts is the actual list (had to use counts_dict to actually count)
        counts = list()
        for k,v in counts_dict.items():
            counts.append([v] + k.split(",")) # split the string representation of the combinations back into list form
        
        # rotate matrix clockwise
        rot = list(zip(*counts[::-1]))
        # rot.sort(key=lambda a: a[0])

        # a bunch of string concatenation
        s = ""
        first = True
        for i in range(len(rot)):
            # for the first line only, no "place" column is necessary and a dashed line will be placed
            if first:
                s += "  | "
                s += " | ".join(str(j) for j in rot[i])
                s += "\n" + "-"*(len(rot[0])*4) + "\n"
                first = False
            else:
                s += "%d | " % i
                s += " | ".join(str(j) for j in rot[i])
                s += "\n"
        return s

    # get candidate list and preference list from filename
    def parse_file(self):
        # get filename and extension
        filename, ext = os.path.splitext(self.file)
        if self.file not in os.listdir('.'):
            raise Exception('File not found.')
        if ext != '.csv':
            raise Exception('File must be csv.')

        # read file
        with open(self.file, 'r') as file:
            candidates = None
            pref_sched = []
            reader = csv.reader(file)

            for row in reader:
                if candidates is None: # get header
                    candidates = list(row)
                else:
                    pref_sched.append(list(row))

        # check if preference schedule is valid
        for i in range(len(pref_sched)):
            pref = pref_sched[i]
            # print(pref)
            if len(pref) != len(candidates):
                raise Exception('Invalid input file; not enough values at line %d.' % (i+2))
            if len(pref) != len(list(set(pref))):
                raise Exception('Invalid input file; duplicate value at line %d.' % (i+2))

        return candidates, pref_sched

######################################################
################## Aggregator Class ##################
######################################################

class Aggregator:

    def __init__(self, p):
        self.prefs = p

    def plurality(self):
        # get info from PreferenceSchedule p
        pref_sched = self.prefs.pref_sched
        candidates = self.prefs.candidates

        # count the number of 1st place votes each candidate received
        counts = {c: 0 for c in candidates}
        for pref in pref_sched:
            counts[pref[0]] += 1

        # print counts
        # for c in counts:
        #     print("%s: %d" % (c, counts[c]))

        # determine the max number of votes any candidate received
        max_votes = max(counts.values())

        # find all candidates who received the max number of votes
        winners = list()
        for c in candidates:
            if counts[c] == max_votes:
                winners.append(c)

        print('Plurality Vote Winner: %s' % ', '.join(winners))
        # print(counts)
        return winners
    
    def borda_count(self):
        # get info from PreferenceSchedule p
        pref_sched = self.prefs.pref_sched
        candidates = self.prefs.candidates

        pref_sched=self.update_pref_sched(pref_sched, 'P')
        candidates=self.update_cand_list(candidates, 'P')

        # count up the ranked votes for each candidate
        counts = {c: 0 for c in candidates}
        num_cands = len(candidates)
        for pref in pref_sched:
            for i in range(num_cands):
                counts[pref[i]] += (num_cands-i) # subtract the index of the vote from the number of votes

        # to print the count results
        for c in counts:
            print("%s:%d" % (c, counts[c]))

        # determine the maximum number of votes any candidate recieved
        max_votes = max(counts.values())

        # find all candidates who recieved the max number of votes
        winners = list()
        for c in candidates:
            if counts[c] == max_votes:
                winners.append(c)

        # print(counts)

        print('Borda Count Winner: %s' % ', '.join(winners))
        return winners
    
    def instant_runoff(self):
        # get info from PreferenceSchedule p
        pref_sched = self.prefs.pref_sched
        candidates = self.prefs.candidates

        # repeat this process forever (aka until a majority is found)
        while True:

            # count 1st place votes for each candidate
            counts = {c: 0 for c in candidates}
            for pref in pref_sched:
                counts[pref[0]] += 1
            
            # print(counts)
            
            # check if there is a majority
            m = self.check_majority(counts)
            if m != None:
                # if there is a majority, return the candidate with the majority
                # print('Winner found!\n')
                print('Instant Runoff Winner: %s' % m)
                return m

            # otherwise, determine the candidates with the fewest majority votes
            min_votes = min(counts.values())
            losers = list()
            for c in candidates:
                if counts[c] == min_votes:
                    losers.append(c)

            # print losers
            # print("removing %s\n" % ", ".join(losers))

            # remove the candidates with the fewest majority votes
            candidates = self.update_cand_list(candidates, losers)
            pref_sched = self.update_pref_sched(pref_sched, losers)

    def condorcet_winner(self):

        candidates = self.prefs.candidates

        counts = {i: 0 for i in candidates}
        combos = [i for i in combinations(candidates, 2)] # each combination 2 candidates to face off
        for combo in combos:
            winner = self.head2head(combo)
            if winner != None:
                counts[winner] += 1 # winner gets a point
            else:
                for j in combo:
                    counts[j] += 0.5 # if it's a tie, each candidate gets 0.5 points
        
        # display counts
        for c in counts:
            print("%s: %d" % (c, counts[c]))

        max_count = max(counts.values())
        winners = list()
        for i in counts:
            if counts[i] == max_count:
                winners.append(i)
        
        print("Condercet Winner: %s" % ", ".join(winners))

    
    def top2approval(self):
        # get info from PreferenceSchedule p
        pref_sched = self.prefs.pref_sched
        candidates = self.prefs.candidates

        # count the number of 1st/2nd place votes each candidate received
        counts = {c: 0 for c in candidates}
        for pref in pref_sched:
            counts[pref[0]] += 1
            counts[pref[1]] += 1

        # print counts
        for c in counts:
            print("%s: %d" % (c, counts[c]))

        # determine the max number of 1st/2nd place votes any candidate received
        max_votes = max(counts.values())

        # find all candidates who received the max number of votes
        winners = list()
        for c in candidates:
            if counts[c] == max_votes:
                winners.append(c)

        print('Top 2 Approval Winner: %s' % ', '.join(winners))
        # print(counts)
        return winners


    def check_majority(self, counts):
        num_votes = sum(counts.values())

        for k,v in counts.items():
            if v/num_votes > 0.5:
                return k
        return None
    
    def update_cand_list(self, cands, losers):
        return [c for c in cands if c not in losers]
    
    def update_pref_sched(self, pref_sched, losers):
        new_sched = list()
        for pref in pref_sched:
            new_sched.append([p for p in pref if p not in losers])
        return new_sched

    def head2head(self, cands):
        a, b = cands
        counts = {a: 0, b: 0}
        for pref in self.prefs.pref_sched:
            if pref.index(a) < pref.index(b):
                counts[a] += 1
            else:
                counts[b] += 1
        
        if counts[a] > counts[b]:
            return a
        elif counts[b] > counts[a]:
            return b
        else:
            return None


if __name__ == '__main__':
    pref_sched = PreferenceSchedule('HP_ranking.csv')
    aggr = Aggregator(pref_sched)

    print()
    # print(pref_sched)
    print()
    # aggr.plurality()
    # aggr.borda_count()
    # aggr.instant_runoff()
    # aggr.condorcet_winner()
    aggr.top2approval()
    print()