all: main.pdf

main.pdf: main.tex
	pdflatex -interaction=nonstopmode main.tex
	bibtex main
# texen mit neuen Referenzen
	pdflatex -interaction=nonstopmode main.tex 
# Jetzt spätestens sollte alles stimmen
	pdflatex -interaction=nonstopmode main.tex 

clean:
	-/bin/rm main.pdf *.out *.lol *.lof *.log *.lot *.aux *.bbl *.toc *.blg
