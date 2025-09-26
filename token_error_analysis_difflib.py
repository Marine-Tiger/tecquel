import difflib
from collections import Counter, defaultdict
import re
import os

class HTRErrorAnalyzer:
    def __init__(self):
        self.error_stats = {
            'substitutions': Counter(),
            'insertions': Counter(), 
            'deletions': Counter()
        }
        self.word_errors = []
        
    def read_file_with_fallback_encoding(self, filepath):
        """Essaie plusieurs encodages pour lire un fichier"""
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    content = f.read().strip()
                    print(f"✓ Fichier '{os.path.basename(filepath)}' lu avec l'encodage {encoding}")
                    return content
            except UnicodeDecodeError:
                continue
        
        raise ValueError(f"Impossible de lire {filepath} avec les encodages testés: {encodings}")
        
    def analyze_texts(self, ground_truth, hypothesis, text_name=""):
        """Analyse les différences entre vérité de terrain et hypothèse HTR"""
        print(f"\n=== Analyse: {text_name} ===")
        print("=" * (15 + len(text_name)))
        
        # Analyse au niveau caractère
        self._analyze_characters(ground_truth, hypothesis)
        
        # Analyse au niveau mot
        self._analyze_words(ground_truth, hypothesis)
        
        # Visualisation HTML des différences
        html_diff = self._generate_html_diff(ground_truth, hypothesis, text_name)
        
        return html_diff
    
    def _analyze_characters(self, gt, hyp):
        """Analyse des erreurs au niveau caractère"""
        print("\n📝 ANALYSE CARACTÈRES")
        print("-" * 40)
        
        # Calcul de la distance de Levenshtein avec détails
        matcher = difflib.SequenceMatcher(None, gt, hyp)
        
        char_errors = {'substitutions': 0, 'insertions': 0, 'deletions': 0}
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                # Substitutions
                gt_chars = gt[i1:i2]
                hyp_chars = hyp[j1:j2]
                char_errors['substitutions'] += max(len(gt_chars), len(hyp_chars))
                
                # Enregistrer les substitutions fréquentes
                for g, h in zip(gt_chars, hyp_chars):
                    if g != h:
                        self.error_stats['substitutions'][f"'{g}' → '{h}'"] += 1
                        
            elif tag == 'delete':
                # Suppressions 
                deleted = gt[i1:i2]
                char_errors['deletions'] += len(deleted)
                for char in deleted:
                    self.error_stats['deletions'][f"'{char}'"] += 1
                    
            elif tag == 'insert':
                # Insertions
                inserted = hyp[j1:j2]
                char_errors['insertions'] += len(inserted)
                for char in inserted:
                    self.error_stats['insertions'][f"'{char}'"] += 1
        
        # Calcul du CER (Character Error Rate)
        total_chars = len(gt)
        total_errors = sum(char_errors.values())
        cer = (total_errors / total_chars) * 100 if total_chars > 0 else 0
        
        print(f"Longueur vérité terrain: {len(gt)} caractères")
        print(f"Longueur hypothèse: {len(hyp)} caractères")
        print(f"CER (Character Error Rate): {cer:.2f}%")
        print(f"Substitutions: {char_errors['substitutions']}")
        print(f"Insertions: {char_errors['insertions']}")
        print(f"Suppressions: {char_errors['deletions']}")
    
    def _analyze_words(self, gt, hyp):
        """Analyse des erreurs au niveau mot"""
        print("\n🔤 ANALYSE MOTS")
        print("-" * 40)
        
        # Tokenisation simple (peut être améliorée selon vos besoins)
        gt_words = re.findall(r'\b\w+\b', gt.lower())
        hyp_words = re.findall(r'\b\w+\b', hyp.lower())
        
        # Alignement des mots
        matcher = difflib.SequenceMatcher(None, gt_words, hyp_words)
        
        word_errors = {'correct': 0, 'substitutions': 0, 'insertions': 0, 'deletions': 0}
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                word_errors['correct'] += (i2 - i1)
            elif tag == 'replace':
                word_errors['substitutions'] += max(i2-i1, j2-j1)
                # Enregistrer les erreurs de mots
                for gt_word, hyp_word in zip(gt_words[i1:i2], hyp_words[j1:j2]):
                    if gt_word != hyp_word:
                        self.word_errors.append({
                            'ground_truth': gt_word,
                            'hypothesis': hyp_word,
                            'error_type': 'substitution'
                        })
            elif tag == 'delete':
                word_errors['deletions'] += (i2 - i1)
                for word in gt_words[i1:i2]:
                    self.word_errors.append({
                        'ground_truth': word,
                        'hypothesis': '',
                        'error_type': 'deletion'
                    })
            elif tag == 'insert':
                word_errors['insertions'] += (j2 - j1)
                for word in hyp_words[j1:j2]:
                    self.word_errors.append({
                        'ground_truth': '',
                        'hypothesis': word,
                        'error_type': 'insertion'
                    })
        
        # Calcul du WER (Word Error Rate)
        total_words = len(gt_words)
        total_word_errors = word_errors['substitutions'] + word_errors['insertions'] + word_errors['deletions']
        wer = (total_word_errors / total_words) * 100 if total_words > 0 else 0
        
        print(f"Nombre de mots (vérité terrain): {len(gt_words)}")
        print(f"Nombre de mots (hypothèse): {len(hyp_words)}")
        print(f"WER (Word Error Rate): {wer:.2f}%")
        print(f"Mots corrects: {word_errors['correct']}")
        print(f"Substitutions de mots: {word_errors['substitutions']}")
        print(f"Insertions de mots: {word_errors['insertions']}")
        print(f"Suppressions de mots: {word_errors['deletions']}")
    
    def _generate_html_diff(self, gt, hyp, model_name=""):
        """Génère une visualisation HTML des différences"""
        differ = difflib.HtmlDiff(tabsize=2)
        html_diff = differ.make_file(
            gt.splitlines(keepends=True),
            hyp.splitlines(keepends=True),
            fromdesc='Vérité de terrain',
            todesc=f'Hypothèse HTR - {model_name}' if model_name else 'Hypothèse HTR',
            context=True,
            numlines=3
        )
        return html_diff
    
    def print_error_summary(self, top_n=10):
        """Affiche un résumé des erreurs les plus fréquentes"""
        print(f"\n🔍 RÉSUMÉ DES ERREURS LES PLUS FRÉQUENTES")
        print("=" * 50)
        
        if self.error_stats['substitutions']:
            print(f"\n📊 Top {top_n} substitutions de caractères:")
            for error, count in self.error_stats['substitutions'].most_common(top_n):
                print(f"  {error}: {count} fois")
        
        if self.error_stats['insertions']:
            print(f"\n➕ Top {top_n} insertions de caractères:")
            for error, count in self.error_stats['insertions'].most_common(top_n):
                print(f"  {error}: {count} fois")
        
        if self.error_stats['deletions']:
            print(f"\n➖ Top {top_n} suppressions de caractères:")
            for error, count in self.error_stats['deletions'].most_common(top_n):
                print(f"  {error}: {count} fois")
        
        if self.word_errors:
            print(f"\n🔤 Erreurs de mots par type:")
            error_by_type = defaultdict(list)
            for error in self.word_errors:
                error_by_type[error['error_type']].append(error)
            
            for error_type, errors in error_by_type.items():
                print(f"\n  {error_type.upper()} ({len(errors)} erreurs):")
                for error in errors[:top_n]:
                    if error_type == 'substitution':
                        print(f"    '{error['ground_truth']}' → '{error['hypothesis']}'")
                    elif error_type == 'deletion':
                        print(f"    '{error['ground_truth']}' → (supprimé)")
                    elif error_type == 'insertion':
                        print(f"    (rien) → '{error['hypothesis']}'")
    
    def reset_stats(self):
        """Remet à zéro les statistiques pour une nouvelle analyse"""
        self.error_stats = {
            'substitutions': Counter(),
            'insertions': Counter(), 
            'deletions': Counter()
        }
        self.word_errors = []

def main():
    analyzer = HTRErrorAnalyzer()
    
    # Chemins vers vos fichiers
    gt_file = "./DATA/ground_truth/R52_1_10p_GT.txt"
    hyp1_file = "./DATA/hypothesis/FT/R52_1_10p_FT.txt"
    hyp2_file = "/DATA/hypothesis/FT/R52_1_10p_FT_postcor.txt"
    
    print("🔍 ANALYSE COMPARATIVE DES SORTIES HTR")
    print("=" * 60)
    
    try:
        # Lecture des fichiers
        print("\n📁 Lecture des fichiers...")
        ground_truth = analyzer.read_file_with_fallback_encoding(gt_file)
        hypothesis1 = analyzer.read_file_with_fallback_encoding(hyp1_file)
        hypothesis2 = analyzer.read_file_with_fallback_encoding(hyp2_file)
        
        print(f"✓ Tous les fichiers ont été lus avec succès")
        
        # Analyse de la première hypothèse
        html_diff1 = analyzer.analyze_texts(ground_truth, hypothesis1, "FT")
        
        # Analyse de la deuxième hypothèse (on garde les stats cumulées)
        html_diff2 = analyzer.analyze_texts(ground_truth, hypothesis2, "FT_postcor")
        
        # Résumé des erreurs cumulées
        analyzer.print_error_summary()
        
        # Sauvegarde des visualisations HTML
        print(f"\n💾 Sauvegarde des visualisations...")
        
        with open('diff_visualization_FT.html', 'w', encoding='utf-8') as f:
            f.write(html_diff1)
            
        with open('diff_visualization_FT_postcor.html', 'w', encoding='utf-8') as f:
            f.write(html_diff2)
            
        print("✓ Visualisations sauvegardées:")
        print("  - diff_visualization_FT.html")
        print("  - diff_visualization_FT_postcor.html")
        print("\nOuvrez ces fichiers dans votre navigateur pour voir les différences en couleur!")
        
    except FileNotFoundError as e:
        print(f"❌ Fichier non trouvé: {e}")
        print("Vérifiez que les chemins des fichiers sont corrects.")
        
    except ValueError as e:
        print(f"❌ Erreur d'encodage: {e}")
        
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()