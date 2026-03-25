a_gap = " gap"
b_gap = " gap"
c_gap = " gap"

score = 0

for soz in a_gap.split():
    if soz in [soz for soz in b_gap]:
        score += 1
        
