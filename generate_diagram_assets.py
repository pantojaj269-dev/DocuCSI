import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs("presentation_assets", exist_ok=True)

def generate_architecture_diagram():
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    ax.set_facecolor("#F8F6F0")
    fig.patch.set_facecolor("#F8F6F0")

    # Boxes
    boxes = [
        {"x": 0.05, "y": 0.55, "w": 0.25, "h": 0.35, "title": "1. PERCEPCIÓN", "sub": "Cámara Web (WebRTC)\nDocumento Digital / Papel", "col": "#1E293B", "text_col": "#FFFFFF"},
        {"x": 0.37, "y": 0.55, "w": 0.26, "h": 0.35, "title": "2. FRONTEND (UI)", "sub": "React 19 + Vite\nTailwind CSS Minimalista", "col": "#0284C7", "text_col": "#FFFFFF"},
        {"x": 0.70, "y": 0.55, "w": 0.26, "h": 0.35, "title": "3. API GATEWAY", "sub": "FastAPI + Uvicorn\nHash SHA-256 Inmutable", "col": "#059669", "text_col": "#FFFFFF"},
        {"x": 0.05, "y": 0.08, "w": 0.58, "h": 0.38, "title": "4. PIPELINE NEURO-SIMBÓLICO (IA & VISIÓN)", "sub": "• OpenCV: Homografía y Esqueletización Zhang-Suen\n• Scikit-Learn: K-Means (Tintas) y Gradient Boosting (Cifras)\n• PyTorch: Red Densa (Firmas) | Algoritmo A* (Cronología)", "col": "#FFFFFF", "text_col": "#1E293B", "edge": "#1E293B"},
        {"x": 0.70, "y": 0.08, "w": 0.26, "h": 0.38, "title": "5. DICTAMEN FINAL", "sub": "Explicabilidad Legal\nInforme Pericial Oficial\nExportación a PDF", "col": "#991B1B", "text_col": "#FFFFFF"}
    ]

    for b in boxes:
        edge = b.get("edge", b["col"])
        rect = patches.FancyBboxPatch(
            (b["x"], b["y"]), b["w"], b["h"],
            boxstyle="round,pad=0.02,rounding_size=0.03",
            facecolor=b["col"], edgecolor=edge, linewidth=1.5
        )
        ax.add_patch(rect)
        ax.text(
            b["x"] + b["w"]/2, b["y"] + b["h"] - 0.09, b["title"],
            ha="center", va="center", color=b["text_col"], fontsize=11, fontweight="bold", fontfamily="sans-serif"
        )
        ax.text(
            b["x"] + b["w"]/2, b["y"] + b["h"]/2 - 0.04, b["sub"],
            ha="center", va="center", color=b["text_col"], fontsize=8.5, fontfamily="sans-serif"
        )

    # Arrows
    arrow_props = dict(arrowstyle="->,head_width=0.4,head_length=0.6", lw=2, color="#334155")
    ax.annotate("", xy=(0.36, 0.72), xytext=(0.31, 0.72), arrowprops=arrow_props)
    ax.annotate("", xy=(0.69, 0.72), xytext=(0.64, 0.72), arrowprops=arrow_props)
    ax.annotate("", xy=(0.34, 0.47), xytext=(0.83, 0.54), arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6", lw=2, color="#334155", connectionstyle="angle,angleA=0,angleB=90,rad=10"))
    ax.annotate("", xy=(0.69, 0.27), xytext=(0.64, 0.27), arrowprops=arrow_props)

    ax.set_xlim(0, 1.01)
    ax.set_ylim(0, 1.0)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig("presentation_assets/architecture_diagram.png", bbox_inches="tight", dpi=300)
    plt.close()
    print("Architecture diagram created.")

def generate_deployment_diagram():
    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
    ax.set_facecolor("#FFFFFF")
    fig.patch.set_facecolor("#FFFFFF")

    # Local Card
    r1 = patches.FancyBboxPatch(
        (0.04, 0.1), 0.43, 0.8,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        facecolor="#F8FAFC", edgecolor="#CBD5E1", linewidth=1.5
    )
    ax.add_patch(r1)
    ax.text(0.255, 0.80, "MODO LOCAL (OFFLINE)", ha="center", va="center", color="#1E293B", fontsize=12, fontweight="bold")
    ax.text(0.255, 0.68, "Estación de Peritaje en Campo", ha="center", va="center", color="#0284C7", fontsize=9.5, fontweight="bold")
    local_txt = "• Inicio automático: iniciar_proyecto.bat\n• Backend: Uvicorn en localhost:8000\n• Frontend: Vite en localhost:5173\n• Sin dependencia de internet\n• Ideal para laptops de investigadores"
    ax.text(0.08, 0.40, local_txt, ha="left", va="center", color="#334155", fontsize=9, linespacing=1.6)

    # Cloud Card
    r2 = patches.FancyBboxPatch(
        (0.53, 0.1), 0.43, 0.8,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        facecolor="#F8FAFC", edgecolor="#CBD5E1", linewidth=1.5
    )
    ax.add_patch(r2)
    ax.text(0.745, 0.80, "MODO NUBE (PRODUCCIÓN)", ha="center", va="center", color="#1E293B", fontsize=12, fontweight="bold")
    ax.text(0.745, 0.68, "Despliegue Institucional", ha="center", va="center", color="#059669", fontsize=9.5, fontweight="bold")
    cloud_txt = "• 100% Contenerizable con Docker\n• Despliegue en AWS, Render o VPS Linux\n• API REST escalable para múltiples juzgados\n• Almacenamiento seguro de evidencias\n• Integrable a sistemas de gestión fiscal"
    ax.text(0.57, 0.40, cloud_txt, ha="left", va="center", color="#334155", fontsize=9, linespacing=1.6)

    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.0)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig("presentation_assets/deployment_diagram.png", bbox_inches="tight", dpi=300)
    plt.close()
    print("Deployment diagram created.")

def generate_conclusion_seal():
    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=300)
    ax.set_facecolor("#FFFFFF")
    fig.patch.set_facecolor("#FFFFFF")

    # Card
    r = patches.FancyBboxPatch(
        (0.05, 0.08), 0.90, 0.84,
        boxstyle="round,pad=0.02,rounding_size=0.04",
        facecolor="#F1F5F9", edgecolor="#059669", linewidth=2.5
    )
    ax.add_patch(r)

    ax.text(0.5, 0.78, "VALIDEZ JURÍDICA AUDITABLE", ha="center", va="center", color="#065F46", fontsize=12, fontweight="bold")
    ax.text(0.5, 0.64, "CADENA DE CUSTODIA DIGITAL", ha="center", va="center", color="#1E293B", fontsize=14, fontweight="bold")

    info = "• Algoritmo Criptográfico: SHA-256 Inmutable\n• Principio de IA Explicable (XAI)\n• Alineado a Normativa Forense ISO/IEC 17025\n• Dictamen con Trazabilidad Completa"
    ax.text(0.12, 0.38, info, ha="left", va="center", color="#334155", fontsize=9.5, linespacing=1.6)

    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.0)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig("presentation_assets/conclusion_seal.png", bbox_inches="tight", dpi=300)
    plt.close()
    print("Conclusion seal created.")

def generate_tech_stack_graphic():
    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
    ax.set_facecolor("#FFFFFF")
    fig.patch.set_facecolor("#FFFFFF")

    techs = [
        {"x": 0.05, "y": 0.53, "w": 0.27, "h": 0.38, "name": "Python & FastAPI", "desc": "API REST Asíncrona\nValidación Pydantic", "col": "#0284C7"},
        {"x": 0.37, "y": 0.53, "w": 0.27, "h": 0.38, "name": "PyTorch (torch)", "desc": "Red Densa (MLP)\nBiomecánica de Firmas", "col": "#EA580C"},
        {"x": 0.69, "y": 0.53, "w": 0.27, "h": 0.38, "name": "OpenCV (cv2)", "desc": "Homografía 4 puntos\nZhang-Suen Esqueleto", "col": "#059669"},
        {"x": 0.05, "y": 0.08, "w": 0.27, "h": 0.38, "name": "Scikit-Learn", "desc": "K-Means, PCA (Tintas)\nGradient Boosting (Cifras)", "col": "#D97706"},
        {"x": 0.37, "y": 0.08, "w": 0.27, "h": 0.38, "name": "React 19 & Vite", "desc": "Frontend SPA Reactivo\nCompilación Instantánea", "col": "#2563EB"},
        {"x": 0.69, "y": 0.08, "w": 0.27, "h": 0.38, "name": "Tailwind CSS 4", "desc": "UI Minimalista Beige\nWebRTC Cámara en Vivo", "col": "#0D9488"},
    ]

    for t in techs:
        card = patches.FancyBboxPatch(
            (t["x"], t["y"]), t["w"], t["h"],
            boxstyle="round,pad=0.02,rounding_size=0.03",
            facecolor="#F8FAFC", edgecolor=t["col"], linewidth=1.8
        )
        ax.add_patch(card)
        ax.text(t["x"] + t["w"]/2, t["y"] + t["h"] - 0.10, t["name"], ha="center", va="center", color="#1E293B", fontsize=11, fontweight="bold")
        ax.text(t["x"] + t["w"]/2, t["y"] + t["h"]/2 - 0.03, t["desc"], ha="center", va="center", color="#475569", fontsize=9, linespacing=1.4)

    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.0)
    ax.axis("off")
    plt.tight_layout()
    plt.savefig("presentation_assets/tech_stack.png", bbox_inches="tight", dpi=300)
    plt.close()
    print("Tech stack graphic created.")

if __name__ == "__main__":
    generate_architecture_diagram()
    generate_deployment_diagram()
    generate_conclusion_seal()
    generate_tech_stack_graphic()
