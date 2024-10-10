import csv
from django.shortcuts import render
from .models import Expert, Candidate, Score
from .forms import UploadCSVForm
from io import TextIOWrapper

def calculate_relevancy(expert_expertise, candidate_expertise):
    expert_skills = set(expert_expertise.split(","))
    candidate_skills = set(candidate_expertise.split(","))
    common_skills = expert_skills.intersection(candidate_skills)
    max_skills = len(expert_skills.union(candidate_skills))
    if max_skills == 0:
        return 0
    relevancy_score = (len(common_skills) / max_skills) * 10  # Score out of 10
    return relevancy_score

def upload_and_match(request):
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            expert_csv = request.FILES['expert_csv']
            candidate_csv = request.FILES['candidate_csv']

            # Clear old records
            Expert.objects.all().delete()
            Candidate.objects.all().delete()
            Score.objects.all().delete()

            # Read and save experts
            experts = []
            expert_file = TextIOWrapper(expert_csv.file, encoding='utf-8')
            reader = csv.DictReader(expert_file)
            for row in reader:
                expert = Expert.objects.create(
                    name=row['name'],
                    expertise=row['expertise']
                )
                experts.append(expert)

            # Read and save candidates
            candidates = []
            candidate_file = TextIOWrapper(candidate_csv.file, encoding='utf-8')
            reader = csv.DictReader(candidate_file)
            for row in reader:
                candidate = Candidate.objects.create(
                    name=row['name'],
                    expertise=row['expertise']
                )
                candidates.append(candidate)

            # Match candidates with experts
            for candidate in candidates:
                best_expert = None
                best_score = 0
                for expert in experts:
                    relevancy_score = calculate_relevancy(expert.expertise, candidate.expertise)
                    if relevancy_score > best_score:
                        best_score = relevancy_score
                        best_expert = expert
                # Save the match and score
                if best_expert:
                    Score.objects.create(expert=best_expert, candidate=candidate, relevancy_score=best_score)

            return render(request, 'core/results.html', {'scores': Score.objects.all()})
    else:
        form = UploadCSVForm()
    
    return render(request, 'core/upload.html', {'form': form})
