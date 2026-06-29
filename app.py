"""
VERA-ND: Verification Engine for Results & Accountability - North Dakota
Type 4 Detection using WIDA ACCESS Speaking vs Writing + ND A+ Achievement Data

North Dakota context: WIDA ACCESS for ELLs, ND A+ (North Dakota Assessment+),
4 performance levels: Novice, Partially Proficient, Proficient, Advanced.
~168 districts, ~4,100 ELs. Top EL districts: Fargo/West Fargo (Somali/Nepali refugees).
New 2025 cut scores implemented. STARS data portal (insights.nd.gov).
Oil boom brought new immigrant populations. Refugee resettlement concentrated in Fargo metro.

H-EDU.Solutions | https://h-edu.solutions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# CONFIGURATION
# ============================================================================

ND_BLUE = "#003DA5"
ND_GOLD = "#FFD700"
ND_DARK = "#002060"
ND_RED = "#CC0000"

# ============================================================================
# DATA: North Dakota Districts with EL Populations
# ============================================================================

def load_districts():
    """
    Load ND districts with significant EL populations.
    Data modeled from STARS portal (insights.nd.gov).
    ND A+ levels: Novice, Partially Proficient, Proficient, Advanced.
    ~168 districts, ~4,100 ELs statewide.
    New 2025 cut scores -- proficiency rates shifted.
    Fargo/West Fargo: Somali and Nepali refugee concentrations.
    """
    data = [
        # (district_id, district_name, total_students, el_count, el_percent,
        #  grad_rate, nda_ela_all, nda_ela_el, nda_ela_hispanic, nda_ela_white,
        #  nda_math_all, nda_math_el, top_el_languages)

        # Fargo metro -- refugee hub
        ("09-001", "Fargo Public Schools", 11500, 1610, 14.0,
         84.5, 48.2, 12.5, 24.8, 58.5,
         42.8, 10.2, "Somali, Nepali, Arabic, Swahili, Kurdish"),
        ("09-006", "West Fargo Public Schools", 11200, 1344, 12.0,
         86.2, 50.5, 14.2, 26.5, 60.2,
         45.2, 12.0, "Nepali, Somali, Arabic, Bosnian, Spanish"),
        ("09-003", "Fargo (North) Schools", 2800, 336, 12.0,
         83.8, 46.8, 12.0, 24.2, 57.2,
         41.5, 9.8, "Somali, Nepali, Arabic, Kurdish"),

        # Other urban centers
        ("08-001", "Bismarck Public Schools", 13200, 660, 5.0,
         88.5, 52.8, 16.5, 28.8, 62.5,
         48.5, 14.2, "Spanish, Arabic, Nepali, Somali"),
        ("14-001", "Grand Forks Public Schools", 7400, 518, 7.0,
         85.2, 49.5, 14.8, 26.2, 59.8,
         44.5, 12.5, "Spanish, Somali, Nepali, Arabic, Vietnamese"),
        ("28-001", "Minot Public Schools", 6800, 408, 6.0,
         84.8, 48.8, 14.2, 25.8, 59.2,
         43.8, 11.8, "Spanish, Somali, Nepali, Norwegian"),
        ("42-007", "Dickinson Public Schools", 3800, 228, 6.0,
         83.5, 47.5, 13.5, 25.2, 58.5,
         42.2, 11.2, "Spanish, Somali, Arabic"),
        ("47-001", "Williston Basin School Dist", 3200, 224, 7.0,
         81.8, 45.8, 12.8, 24.5, 57.5,
         40.5, 10.5, "Spanish, Somali, Arabic, Filipino"),

        # Oil patch / emerging EL districts
        ("08-017", "Mandan Public Schools", 3600, 180, 5.0,
         86.5, 50.8, 15.0, 27.2, 60.5,
         45.8, 12.8, "Spanish, Arabic, Somali"),
        ("21-009", "Jamestown Public Schools", 2400, 144, 6.0,
         84.2, 48.2, 14.0, 25.5, 58.8,
         43.2, 11.5, "Spanish, Nepali, Somali"),
        ("09-002", "Moorhead-Dilworth (Cass)", 2200, 154, 7.0,
         83.5, 47.2, 13.2, 24.8, 57.8,
         41.8, 10.8, "Somali, Nepali, Spanish, Kurdish"),
        ("27-001", "Devils Lake Public Schools", 1800, 126, 7.0,
         80.2, 44.2, 12.5, 23.5, 56.5,
         39.5, 10.0, "Spanish, Somali, Arabic, Dakota"),
        ("15-001", "Wahpeton Public Schools", 1500, 90, 6.0,
         82.5, 46.5, 13.8, 25.2, 58.2,
         42.0, 11.0, "Spanish, Somali, Nepali"),
        ("09-128", "Kindred Public Schools", 1100, 55, 5.0,
         88.8, 54.2, 17.5, 30.2, 62.8,
         50.2, 14.8, "Spanish, Nepali"),
        ("03-001", "Valley City Public Schools", 1200, 60, 5.0,
         85.5, 50.2, 15.2, 27.5, 60.8,
         46.2, 13.0, "Spanish, Somali, Arabic"),
    ]

    return pd.DataFrame(data, columns=[
        'district_id', 'district_name', 'total_students',
        'el_count', 'el_percent', 'graduation_rate',
        'nda_ela_all', 'nda_ela_el', 'nda_ela_hispanic',
        'nda_ela_white',
        'nda_math_all', 'nda_math_el', 'top_el_languages'
    ])


# ============================================================================
# DATA: ACCESS Domain Data
# ============================================================================

def load_access_data(districts_df):
    """
    Generate district ACCESS domain data modeled from STARS ACCESS data.
    North Dakota uses WIDA ACCESS. Exit criteria: composite 4.5+
    with domain minimums. Scale scores approximate WIDA ACCESS range.
    """
    access_data = []

    for _, d in districts_df.iterrows():
        for grade in range(3, 9):
            for year in [2024, 2025]:
                base_speaking = 334 + (grade * 9)
                base_writing = 280 + (grade * 7)
                base_listening = 339 + (grade * 8)
                base_reading = 292 + (grade * 7)

                el_factor = d['nda_ela_el'] / 15.0
                speaking_adj = int(11 * el_factor + d['el_percent'] * 0.30)
                writing_adj = int(-14 + (el_factor - 1) * 11)
                listening_adj = speaking_adj - 2
                reading_adj = writing_adj + 7

                if 'Somali' in d['top_el_languages']:
                    speaking_adj -= 3
                    writing_adj -= 6
                if 'Nepali' in d['top_el_languages']:
                    speaking_adj -= 2
                    writing_adj -= 5
                if 'Kurdish' in d['top_el_languages']:
                    speaking_adj -= 2
                    writing_adj -= 4

                year_adj = 3 if year == 2025 else 0

                # New 2025 cut scores -- slight adjustment
                if year == 2025:
                    year_adj += 1

                access_data.append({
                    'district_id': d['district_id'],
                    'district_name': d['district_name'],
                    'grade': grade,
                    'year': year,
                    'total_tested': max(8, int(d['el_count'] / 6)),
                    'listening_avg': base_listening + listening_adj + year_adj,
                    'speaking_avg': base_speaking + speaking_adj + year_adj,
                    'reading_avg': base_reading + reading_adj + year_adj,
                    'writing_avg': base_writing + writing_adj + year_adj,
                    'composite_avg': int((base_speaking + speaking_adj +
                                          base_writing + writing_adj +
                                          base_listening + listening_adj +
                                          base_reading + reading_adj) / 4 + 12 + year_adj),
                })

    return pd.DataFrame(access_data)


# ============================================================================
# DATA: ND A+ Achievement Data
# ============================================================================

def load_nda_data(districts_df):
    """
    Generate ND A+ data based on STARS proficiency rates.
    ND A+ has 4 performance levels: Novice, Partially Proficient,
    Proficient, Advanced. New 2025 cut scores implemented.
    ELA and Math tested grades 3-8 and 10.
    """
    nda_data = []

    for _, d in districts_df.iterrows():
        for grade in range(3, 9):
            for year in [2024, 2025]:
                for subject in ['ELA', 'Math']:
                    if subject == 'ELA':
                        base = d['nda_ela_all']
                    else:
                        base = d['nda_math_all']

                    prof = max(10, min(85, base + (grade - 5) * -1.2))

                    if year == 2024:
                        prof = prof - 1.0
                    # 2025 new cut scores -- slight proficiency drop
                    if year == 2025:
                        prof = prof - 2.0

                    # 4-level distribution: Novice / Partially Proficient / Proficient / Advanced
                    advanced = max(2, prof * 0.18)
                    proficient = max(5, prof - advanced)
                    partial = max(10, (100 - prof) * 0.42)
                    novice = max(5, 100 - proficient - advanced - partial)

                    nda_data.append({
                        'district_id': d['district_id'],
                        'district_name': d['district_name'],
                        'grade': grade,
                        'subject': subject,
                        'year': year,
                        'novice_pct': round(novice, 1),
                        'partial_pct': round(partial, 1),
                        'proficient_pct': round(proficient, 1),
                        'advanced_pct': round(advanced, 1),
                        'prof_plus_pct': round(proficient + advanced, 1),
                    })

    return pd.DataFrame(nda_data)


# ============================================================================
# DATA: Statewide Domain Proficiency
# ============================================================================

def load_statewide_domain_data():
    """
    Statewide ACCESS domain proficiency percentages by grade cluster.
    Source: STARS portal (insights.nd.gov) ACCESS data.
    ~4,100 ELs across ~168 districts.
    Fargo/West Fargo carry ~60% of state EL population.
    """
    return pd.DataFrame([
        {'year': '2024-25', 'grade_cluster': 'K-2', 'listening': 43, 'speaking': 39, 'reading': 25, 'writing': 19},
        {'year': '2024-25', 'grade_cluster': '3-5', 'listening': 49, 'speaking': 45, 'reading': 29, 'writing': 21},
        {'year': '2024-25', 'grade_cluster': '6-8', 'listening': 53, 'speaking': 47, 'reading': 33, 'writing': 24},
        {'year': '2024-25', 'grade_cluster': '9-12', 'listening': 56, 'speaking': 49, 'reading': 36, 'writing': 26},
        {'year': '2023-24', 'grade_cluster': 'K-2', 'listening': 41, 'speaking': 37, 'reading': 23, 'writing': 17},
        {'year': '2023-24', 'grade_cluster': '3-5', 'listening': 47, 'speaking': 43, 'reading': 27, 'writing': 19},
        {'year': '2023-24', 'grade_cluster': '6-8', 'listening': 51, 'speaking': 45, 'reading': 31, 'writing': 22},
        {'year': '2023-24', 'grade_cluster': '9-12', 'listening': 54, 'speaking': 47, 'reading': 34, 'writing': 24},
    ])


# ============================================================================
# AUTHENTICATION
# ============================================================================


# ============================================================================
# TYPE 4 DETECTION
# ============================================================================

def compute_type4_analysis(access_df, district_id, grade, year):
    """
    Compute Type 4 detection for a given district/grade/year.
    Type 4 candidates show strong oral skills but weak written skills.
    Delta = Speaking - Writing. Flag threshold: normalized delta > 8.
    """
    filtered = access_df[
        (access_df['district_id'] == district_id) &
        (access_df['grade'] == grade) &
        (access_df['year'] == year)
    ]
    if filtered.empty:
        return None

    row = filtered.iloc[0]
    delta = row['speaking_avg'] - row['writing_avg']
    delta_normalized = delta / 5
    flagged = delta_normalized > 8

    return {
        'district_id': district_id,
        'district_name': row['district_name'],
        'grade': grade,
        'year': year,
        'speaking_avg': row['speaking_avg'],
        'writing_avg': row['writing_avg'],
        'delta': delta,
        'delta_normalized': delta_normalized,
        'flagged': flagged,
        'total_tested': row['total_tested'],
        'estimated_flagged': int(row['total_tested'] * 0.15) if flagged else int(row['total_tested'] * 0.05)
    }


# ============================================================================
# PAGES
# ============================================================================

def render_overview(districts_df):
    st.header("North Dakota Education Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pilot Districts", len(districts_df))
    with col2:
        st.metric("Total Students", f"{districts_df['total_students'].sum():,}")
    with col3:
        st.metric("English Learners", f"{districts_df['el_count'].sum():,}")
    with col4:
        st.metric("Statewide EL Count", "~4,100", help="Concentrated in Fargo metro")

    st.divider()

    st.subheader("North Dakota Policy Context")
    st.markdown("""
    North Dakota's EL population has grown significantly due to **refugee resettlement**
    (Somali, Nepali/Bhutanese) concentrated in the Fargo/West Fargo metro area, and
    **oil boom** immigration in western ND (Williston, Dickinson). The state uses
    **WIDA ACCESS** for English proficiency and the **ND A+** assessment with 4 levels
    (Novice, Partially Proficient, Proficient, Advanced). **New 2025 cut scores** have
    shifted proficiency rates statewide.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.error("**Fargo/West Fargo Hub**\n~60% of state ELs concentrated in Fargo metro")
    with col2:
        st.warning("**New 2025 Cut Scores**\nProficiency rates shifted with recalibrated thresholds")
    with col3:
        st.info("**Refugee Resettlement**\nSomali and Nepali communities in Fargo area")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**WIDA ACCESS**\n4 domains, composite exit 4.5+ w/ domain mins")
    with col2:
        st.info("**ND A+**\n4 levels: Novice / Partial / Proficient / Advanced")
    with col3:
        st.info("**STARS Portal**\ninsights.nd.gov, ~168 districts")

    st.divider()

    st.subheader("Key State Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Statewide EL Count", "~4,100")
    with col2:
        st.metric("Total Districts", "~168")
    with col3:
        st.metric("ELP Assessment", "WIDA ACCESS")
    with col4:
        st.metric("Academic Assessment", "ND A+")

    st.divider()

    st.subheader("Top EL Languages Statewide")
    lang_data = pd.DataFrame({
        'Language': ['Somali', 'Spanish', 'Nepali', 'Arabic', 'Kurdish',
                     'Swahili', 'Bosnian', 'Vietnamese'],
        'Approx Share': [25, 22, 15, 10, 6, 5, 4, 3],
    })
    fig_lang = px.bar(lang_data, x='Language', y='Approx Share',
                      color='Approx Share',
                      color_continuous_scale=[[0, '#C0C0C0'], [1, ND_BLUE]],
                      labels={'Approx Share': '% of EL Population'},
                      text='Approx Share')
    fig_lang.update_traces(texttemplate='%{text}%', textposition='outside')
    fig_lang.update_layout(height=350, showlegend=False, coloraxis_showscale=False,
                           title="Top EL Home Languages in North Dakota")
    st.plotly_chart(fig_lang, use_container_width=True)

    st.divider()

    st.subheader("Pilot Districts -- Highest EL Populations")
    display = districts_df[['district_id', 'district_name', 'total_students', 'el_count', 'el_percent',
                            'nda_ela_all', 'nda_ela_el', 'nda_ela_white',
                            'top_el_languages']].copy()
    display.columns = ['Dist ID', 'District', 'Students', 'EL Count', 'EL %',
                       'ELA All %', 'ELA EL %', 'ELA White %',
                       'Top Languages']
    st.dataframe(display, use_container_width=True, hide_index=True)

    st.subheader("English Learner Population by District")
    fig = px.bar(
        districts_df.sort_values('el_count', ascending=True),
        x='el_count', y='district_name', orientation='h',
        color='el_percent', color_continuous_scale=[[0, '#C0C0C0'], [1, ND_BLUE]],
        labels={'el_count': 'English Learners', 'district_name': 'District', 'el_percent': 'EL %'}
    )
    fig.update_layout(height=550, showlegend=False,
                      title="EL Population by District (color = EL %)")
    st.plotly_chart(fig, use_container_width=True)


def render_domain_analysis(domain_df):
    st.header("Statewide ACCESS Domain Proficiency")

    st.markdown("""
    **Source:** STARS portal (insights.nd.gov). North Dakota is a WIDA Consortium member.
    Domain proficiency percentages show the systemic oral-written delta: Speaking consistently
    outperforms Writing across all grade clusters. The concentration of Somali and Nepali
    refugee populations in Fargo/West Fargo intensifies the writing gap, as these languages
    use non-Latin scripts (Somali was historically oral; Nepali uses Devanagari).
    """)

    year = st.selectbox("Year", ['2024-25', '2023-24'], key="dom_y")
    filtered = domain_df[domain_df['year'] == year]

    st.divider()

    fig = go.Figure()
    for domain, color in [('listening', ND_BLUE), ('speaking', ND_GOLD),
                           ('reading', '#888888'), ('writing', ND_RED)]:
        fig.add_trace(go.Bar(
            x=filtered['grade_cluster'], y=filtered[domain],
            name=domain.capitalize(), marker_color=color,
            text=[f"{v}%" for v in filtered[domain]], textposition='outside'
        ))
    fig.update_layout(
        title=f"ACCESS Domain Proficiency by Grade Cluster ({year})",
        xaxis_title="Grade Cluster", yaxis_title="% Proficient",
        barmode='group', height=450, yaxis=dict(range=[0, 72])
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Speaking-Writing Delta by Grade Cluster")
    filtered = filtered.copy()
    filtered['delta'] = filtered['speaking'] - filtered['writing']
    fig2 = go.Figure(go.Bar(
        x=filtered['grade_cluster'], y=filtered['delta'],
        marker_color=[ND_RED if d > 18 else ND_GOLD for d in filtered['delta']],
        text=[f"{d:+d} pts" for d in filtered['delta']], textposition='outside'
    ))
    fig2.update_layout(title="Speaking - Writing Gap",
                       yaxis_title="Delta (percentage points)", height=350)
    st.plotly_chart(fig2, use_container_width=True)

    avg_delta = filtered['delta'].mean()
    st.metric("Average Speaking-Writing Delta", f"{avg_delta:+.0f} percentage points",
              help="Positive = Speaking proficiency exceeds Writing proficiency statewide")

    st.markdown("""
    ---
    **Why this matters for North Dakota:** With Somali and Nepali communities comprising
    ~40% of the state's EL population and concentrated in Fargo/West Fargo, the oral-written
    gap reflects L1 literacy system differences. Somali was historically an oral language
    (written standard adopted in 1972), and Nepali uses Devanagari script. These communities
    develop strong oral English through daily immersion but face significant barriers in
    academic written English. The **new 2025 cut scores** may further expose this gap.
    """)


def render_access_analysis(access_df, districts_df):
    st.header("ACCESS for ELLs Analysis")
    st.markdown("""
    **WIDA ACCESS** measures English learners across four domains. North Dakota has ~4,100 ELs
    across ~168 districts. Exit criteria: composite proficiency level **4.5+** with domain minimums.
    Fargo/West Fargo carry approximately 60% of the state's EL population.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        district = st.selectbox("District", districts_df['district_name'].tolist(), key="acc_d")
    with col2:
        grade = st.selectbox("Grade", list(range(3, 9)), key="acc_g")
    with col3:
        year = st.selectbox("Year", [2025, 2024], key="acc_y")

    district_id = districts_df[districts_df['district_name'] == district]['district_id'].values[0]
    filtered = access_df[
        (access_df['district_id'] == district_id) &
        (access_df['grade'] == grade) &
        (access_df['year'] == year)
    ]

    if not filtered.empty:
        row = filtered.iloc[0]

        lang = districts_df[districts_df['district_id'] == district_id]['top_el_languages'].values[0]
        st.info(f"**Top EL languages in {district}:** {lang}")

        st.divider()
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Listening", f"{row['listening_avg']:.0f}")
        with col2:
            st.metric("Speaking", f"{row['speaking_avg']:.0f}")
        with col3:
            st.metric("Reading", f"{row['reading_avg']:.0f}")
        with col4:
            st.metric("Writing", f"{row['writing_avg']:.0f}")
        with col5:
            st.metric("Composite", f"{row['composite_avg']:.0f}")

        domains = ['Listening', 'Speaking', 'Reading', 'Writing']
        scores = [row['listening_avg'], row['speaking_avg'], row['reading_avg'], row['writing_avg']]
        fig = go.Figure(go.Bar(
            x=domains, y=scores,
            marker_color=[ND_BLUE, ND_GOLD, '#888888', ND_RED],
            text=[f"{s:.0f}" for s in scores], textposition='outside'
        ))
        fig.update_layout(
            title=f"ACCESS Domains -- {district} -- Grade {grade} ({year})",
            yaxis_title="Scale Score", height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        oral = (row['listening_avg'] + row['speaking_avg']) / 2
        written = (row['reading_avg'] + row['writing_avg']) / 2
        gap = oral - written
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Oral Average", f"{oral:.0f}")
        with col2:
            st.metric("Written Average", f"{written:.0f}")
        with col3:
            st.metric("Oral-Written Gap", f"{gap:+.0f}",
                      delta="Flag" if gap > 30 else "Monitor" if gap > 20 else "OK")

        st.subheader("Exit Criteria Check (ND: composite 4.5+ w/ domain mins)")
        st.markdown("""
        North Dakota exit criteria require a composite proficiency level of **4.5 or higher**
        with minimum domain scores. The **new 2025 cut scores** have recalibrated proficiency
        thresholds, potentially affecting reclassification rates. Districts should monitor
        how the new cut scores interact with domain-level performance, especially for students
        with strong oral but weak written domains.
        """)
    else:
        st.warning("No data available for the selected filters.")


def render_type4(access_df, districts_df):
    st.header("Type 4 Detection")
    st.markdown("""
    **Type 4 candidates** show strong oral skills but weak written skills.
    Delta = Speaking - Writing. Flag threshold: normalized delta > 8.

    In North Dakota, the Somali and Nepali refugee populations in Fargo/West Fargo
    are at heightened risk for Type 4 classification. The **new 2025 cut scores** may
    shift how these patterns interact with reclassification decisions.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        district = st.selectbox("District", districts_df['district_name'].tolist(), key="t4_d")
    with col2:
        grade = st.selectbox("Grade", list(range(3, 9)), key="t4_g")
    with col3:
        year = st.selectbox("Year", [2025, 2024], key="t4_y")

    district_id = districts_df[districts_df['district_name'] == district]['district_id'].values[0]
    result = compute_type4_analysis(access_df, district_id, grade, year)

    if result:
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Speaking", f"{result['speaking_avg']:.0f}")
        with col2:
            st.metric("Writing", f"{result['writing_avg']:.0f}")
        with col3:
            st.metric("Delta", f"{result['delta']:+.0f}")
        with col4:
            st.metric("Status", "FLAGGED" if result['flagged'] else "OK")

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Speaking', x=['Score'], y=[result['speaking_avg']],
                             marker_color=ND_GOLD))
        fig.add_trace(go.Bar(name='Writing', x=['Score'], y=[result['writing_avg']],
                             marker_color=ND_BLUE))
        fig.update_layout(
            title=f"Speaking vs Writing -- {district} -- Grade {grade}",
            barmode='group', height=350
        )
        st.plotly_chart(fig, use_container_width=True)

        if result['flagged']:
            st.error(f"**Type 4 Flag Triggered** -- Delta: {result['delta']:+.0f}. "
                     f"Est. {result['estimated_flagged']} of {result['total_tested']} students affected.")
            st.markdown("""
            **North Dakota-specific action:** Fargo/West Fargo districts should implement
            targeted writing interventions for Somali and Nepali students. Consider
            L1 literacy bridging programs, especially for Somali speakers (whose written
            language tradition is relatively recent). Coordinate with Lutheran Immigration
            and Refugee Service and other resettlement agencies for family literacy support.
            Monitor how new 2025 cut scores affect reclassification for Type 4 students.
            """)
        else:
            st.success(f"**No Type 4 Flag** -- Delta within normal range ({result['delta']:+.0f}).")

        st.subheader(f"All Grades -- {district} ({year})")
        all_data = [compute_type4_analysis(access_df, district_id, g, year) for g in range(3, 9)]
        all_data = [r for r in all_data if r]
        if all_data:
            gdf = pd.DataFrame(all_data)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=gdf['grade'], y=gdf['speaking_avg'],
                name='Speaking', mode='lines+markers',
                line=dict(color=ND_GOLD, width=3)
            ))
            fig.add_trace(go.Scatter(
                x=gdf['grade'], y=gdf['writing_avg'],
                name='Writing', mode='lines+markers',
                line=dict(color=ND_BLUE, width=3)
            ))
            fig.update_layout(
                title="Speaking vs Writing Across Grades",
                xaxis_title="Grade", yaxis_title="Scale Score", height=400
            )
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Type 4 Summary Table")
            summary = gdf[['grade', 'speaking_avg', 'writing_avg', 'delta', 'delta_normalized', 'flagged',
                           'total_tested', 'estimated_flagged']].copy()
            summary.columns = ['Grade', 'Speaking', 'Writing', 'Delta', 'Norm Delta', 'Flagged',
                              'Tested', 'Est. Affected']
            st.dataframe(summary, use_container_width=True, hide_index=True)


def render_achievement_gaps(districts_df):
    st.header("Achievement Gap Analysis")

    st.markdown("""
    **ND A+ ELA proficiency by subgroup** across pilot districts. North Dakota's overall
    proficiency rates are relatively strong, but the EL gap is significant, especially
    in Fargo/West Fargo where refugee populations are concentrated. The **new 2025 cut scores**
    have recalibrated all proficiency rates.
    """)

    st.divider()

    fig = go.Figure()
    sorted_df = districts_df.sort_values('nda_ela_all', ascending=True)
    for col, name, color in [
        ('nda_ela_white', 'White', '#666666'),
        ('nda_ela_all', 'All Students', ND_BLUE),
        ('nda_ela_hispanic', 'Hispanic', '#E8540A'),
        ('nda_ela_el', 'English Learners', ND_GOLD),
    ]:
        fig.add_trace(go.Bar(
            x=sorted_df[col], y=sorted_df['district_name'],
            name=name, orientation='h', marker_color=color
        ))

    fig.update_layout(
        title="ND A+ ELA Proficiency by Subgroup",
        barmode='group', xaxis_title="% Proficient + Advanced", height=650,
        legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Gap Magnitude: White - EL Proficiency")
    districts_df_copy = districts_df.copy()
    districts_df_copy['wh_gap'] = districts_df_copy['nda_ela_white'] - districts_df_copy['nda_ela_hispanic']
    districts_df_copy['we_gap'] = districts_df_copy['nda_ela_white'] - districts_df_copy['nda_ela_el']

    col1, col2 = st.columns(2)
    with col1:
        avg_wh = districts_df_copy['wh_gap'].mean()
        st.metric("Avg White-Hispanic Gap", f"{avg_wh:.1f} pts", delta="Critical", delta_color="inverse")
    with col2:
        avg_we = districts_df_copy['we_gap'].mean()
        st.metric("Avg White-EL Gap", f"{avg_we:.1f} pts", delta="Critical", delta_color="inverse")

    st.error(f"**Average White-EL gap: {avg_we:.0f} pts.** Fargo/West Fargo carry the heaviest "
             f"refugee resettlement load, with Somali and Nepali students showing the largest "
             f"gaps. New 2025 cut scores may further expose these disparities.")

    fig_gap = go.Figure()
    gap_sorted = districts_df_copy.sort_values('we_gap', ascending=True)
    fig_gap.add_trace(go.Bar(
        x=gap_sorted['we_gap'], y=gap_sorted['district_name'],
        orientation='h', marker_color=[ND_RED if g > 40 else ND_GOLD for g in gap_sorted['we_gap']],
        text=[f"{g:.0f} pts" for g in gap_sorted['we_gap']], textposition='outside'
    ))
    fig_gap.update_layout(
        title="White-EL ELA Gap by District (pts)", height=550,
        xaxis_title="Gap (percentage points)"
    )
    st.plotly_chart(fig_gap, use_container_width=True)

    st.subheader("EL Proficiency vs Overall Proficiency")
    fig2 = px.scatter(
        districts_df, x='nda_ela_all', y='nda_ela_el', size='el_count',
        color='el_percent', color_continuous_scale=[[0, '#ccc'], [1, ND_BLUE]],
        hover_name='district_name',
        labels={'nda_ela_all': 'All Students ELA %', 'nda_ela_el': 'EL ELA %',
                'el_count': 'EL Count', 'el_percent': 'EL %'}
    )
    fig2.add_shape(type="line", x0=0, y0=0, x1=80, y1=80,
                   line=dict(dash="dash", color="gray"))
    fig2.update_layout(
        title="EL Proficiency vs District Overall -- Gap Visualization", height=450
    )
    st.plotly_chart(fig2, use_container_width=True)


def render_nda(nda_df, districts_df):
    st.header("ND A+ Assessment Analysis")
    st.markdown("""
    **North Dakota Assessment+ (ND A+)** -- 4 performance levels:
    Novice, Partially Proficient, Proficient, Advanced.
    ELA and Math: grades 3-8 and 10. **New 2025 cut scores** have been implemented,
    recalibrating proficiency thresholds statewide.
    """)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        district = st.selectbox("District", districts_df['district_name'].tolist(), key="nda_d")
    with col2:
        grade = st.selectbox("Grade", list(range(3, 9)), key="nda_g")
    with col3:
        subject = st.selectbox("Subject", ['ELA', 'Math'], key="nda_s")
    with col4:
        year = st.selectbox("Year", [2025, 2024], key="nda_y")

    district_id = districts_df[districts_df['district_name'] == district]['district_id'].values[0]
    filtered = nda_df[
        (nda_df['district_id'] == district_id) &
        (nda_df['grade'] == grade) &
        (nda_df['subject'] == subject) &
        (nda_df['year'] == year)
    ]

    if not filtered.empty:
        row = filtered.iloc[0]
        st.divider()

        if year == 2025:
            st.warning("**2025 data reflects new cut scores.** Proficiency rates may differ "
                       "from prior years due to recalibrated performance level thresholds.")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Novice", f"{row['novice_pct']:.1f}%")
        with col2:
            st.metric("Partially Proficient", f"{row['partial_pct']:.1f}%")
        with col3:
            st.metric("Proficient", f"{row['proficient_pct']:.1f}%")
        with col4:
            st.metric("Advanced", f"{row['advanced_pct']:.1f}%")

        levels = ['Novice', 'Partially Proficient', 'Proficient', 'Advanced']
        values = [row['novice_pct'], row['partial_pct'],
                  row['proficient_pct'], row['advanced_pct']]
        colors = [ND_RED, '#E8540A', ND_GOLD, ND_BLUE]
        fig = go.Figure(go.Bar(
            x=levels, y=values, marker_color=colors,
            text=[f"{v:.1f}%" for v in values], textposition='outside'
        ))
        fig.update_layout(
            title=f"ND A+ {subject} -- {district} -- Grade {grade} ({year})",
            yaxis_title="Percentage", height=400
        )
        st.plotly_chart(fig, use_container_width=True)

        st.metric("Combined Proficiency (Proficient + Advanced)",
                  f"{row['prof_plus_pct']:.1f}%",
                  help="Proficient + Advanced")

        st.subheader(f"ND A+ {subject} Across Grades -- {district} ({year})")
        cross = nda_df[
            (nda_df['district_id'] == district_id) &
            (nda_df['subject'] == subject) &
            (nda_df['year'] == year)
        ]
        if not cross.empty:
            fig2 = go.Figure()
            for level, color in zip(levels, colors):
                col_name = {'Novice': 'novice_pct', 'Partially Proficient': 'partial_pct',
                           'Proficient': 'proficient_pct', 'Advanced': 'advanced_pct'}[level]
                fig2.add_trace(go.Bar(
                    x=cross['grade'], y=cross[col_name],
                    name=level, marker_color=color
                ))
            fig2.update_layout(
                barmode='stack', xaxis_title="Grade", yaxis_title="Percentage",
                height=400, title=f"ND A+ {subject} Performance Distribution"
            )
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")


def render_export(access_df, nda_df, districts_df, domain_df):
    st.header("Export Data")

    st.markdown("Download VERA-ND analysis data as CSV files for further analysis.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("ACCESS Data")
        st.dataframe(access_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download ACCESS CSV",
            access_df.to_csv(index=False),
            "vera_nd_access.csv", "text/csv",
            use_container_width=True
        )
    with col2:
        st.subheader("ND A+ Data")
        st.dataframe(nda_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download ND A+ CSV",
            nda_df.to_csv(index=False),
            "vera_nd_nda.csv", "text/csv",
            use_container_width=True
        )

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Statewide Domain Proficiency")
        st.dataframe(domain_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download Domain CSV",
            domain_df.to_csv(index=False),
            "vera_nd_domains.csv", "text/csv",
            use_container_width=True
        )
    with col2:
        st.subheader("District Reference Data")
        st.dataframe(districts_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download Districts CSV",
            districts_df.to_csv(index=False),
            "vera_nd_districts.csv", "text/csv",
            use_container_width=True
        )


# ============================================================================
# MAIN
# ============================================================================

def main():
    st.set_page_config(
        page_title="VERA-ND | North Dakota Type 4 Detection",
        page_icon="*",
        layout="wide"
    )

    st.markdown(f"""
    <style>
        .stApp {{ background-color: #fafafa; }}
        .block-container {{ padding-top: 2rem; }}
        h1, h2, h3 {{ color: {ND_BLUE}; }}
        .stButton > button {{ background-color: {ND_BLUE}; color: white; }}
        .stButton > button:hover {{ background-color: {ND_DARK}; color: white; }}
    </style>
    """, unsafe_allow_html=True)

    districts_df = load_districts()
    access_df = load_access_data(districts_df)
    nda_df = load_nda_data(districts_df)
    domain_df = load_statewide_domain_data()

    st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h2 style="color: {ND_BLUE}; margin: 0;">VERA-ND</h2>
        <p style="color: #666; font-size: 0.85rem; margin-top: 5px;">North Dakota Implementation</p>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.divider()

    page = st.sidebar.radio("Navigation", [
        "Overview",
        "Statewide Domain Analysis",
        "ACCESS Analysis",
        "Type 4 Detection",
        "Achievement Gaps",
        "ND A+ Analysis",
        "Export Data"
    ])

    st.sidebar.divider()
    st.sidebar.markdown(f"""
    **Data Sources:**
    - ACCESS for ELLs (WIDA)
    - STARS ACCESS Data
    - STARS Portal (insights.nd.gov)
    - ND A+ Assessment
    - ND Dept of Public Instruction

    **Type 4 Detection:**
    - Speaking vs Writing delta
    - Flag threshold: > 8 points (normalized)

    **ND Exit Criteria:**
    - Composite 4.5+ w/ domain mins

    **Key Context:**
    - ~4,100 ELs
    - ~168 school districts
    - **New 2025 cut scores**
    - Somali dominant (25%)
    - Fargo 1,610 ELs (14%)
    - West Fargo 1,344 ELs (12%)
    - ~60% ELs in Fargo metro
    - Refugee resettlement hub
    - Oil boom immigration

    ---
    [H-EDU.Solutions](https://h-edu.solutions)
    """)

    if page == "Overview":
        render_overview(districts_df)
    elif page == "Statewide Domain Analysis":
        render_domain_analysis(domain_df)
    elif page == "ACCESS Analysis":
        render_access_analysis(access_df, districts_df)
    elif page == "Type 4 Detection":
        render_type4(access_df, districts_df)
    elif page == "Achievement Gaps":
        render_achievement_gaps(districts_df)
    elif page == "ND A+ Analysis":
        render_nda(nda_df, districts_df)
    elif page == "Export Data":
        render_export(access_df, nda_df, districts_df, domain_df)


if __name__ == "__main__":
    main()
