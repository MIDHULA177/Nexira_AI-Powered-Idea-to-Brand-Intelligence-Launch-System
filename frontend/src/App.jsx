import { useMemo, useState } from 'react'
import api from './services/api'

const initialForm = {
  description: 'An AI platform that helps college students find teammates for hackathons based on skills and interests.',
  audience: 'college students',
  industry: 'education technology'
}

function App() {
  const [form, setForm] = useState(initialForm)
  const [projectId, setProjectId] = useState('')
  const [loading, setLoading] = useState(false)
  const [stage, setStage] = useState('landing')
  const [project, setProject] = useState(null)
  const [error, setError] = useState('')

  const stageSteps = useMemo(() => [
    'Discover',
    'Position',
    'Shape',
    'Visualize',
    'Challenge',
    'Consistency',
    'Deliver'
  ], [])

  const updateField = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const createProject = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await api.post('/project', {
        description: form.description,
        audience: form.audience,
        industry: form.industry
      })
      setProjectId(response.data.project_id)
      setProject(response.data.project)
      setStage('discover')
      await runWorkflow('discover', response.data.project_id)
    } catch (err) {
      setError('Unable to create the project. Please check the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const runWorkflow = async (step, id = projectId) => {
    if (!id) return
    setLoading(true)
    setError('')
    try {
      const response = await api.post(`/workflow/${step}`, { project_id: id })
      const nextProject = { ...project, ...response.data }
      setProject(nextProject)
      if (step === 'discover') setStage('position')
      if (step === 'position') setStage('shape')
      if (step === 'shape') setStage('visualize')
      if (step === 'visualize') setStage('challenge')
      if (step === 'challenge') setStage('consistency')
      if (step === 'consistency') setStage('deliver')
      if (step === 'deliver') setStage('final')
      if (response.data.final_brand) setProject((prev) => ({ ...prev, final_brand: response.data.final_brand }))
      if (step !== 'deliver') {
        const nextStep = {
          discover: 'position',
          position: 'shape',
          shape: 'visualize',
          visualize: 'challenge',
          challenge: 'consistency',
          consistency: 'deliver'
        }[step]

        if (nextStep) {
          const nextResponse = await api.post(`/workflow/${nextStep}`, { project_id: id })
          const updatedProject = { ...project, ...nextResponse.data }
          setProject(updatedProject)
          if (nextStep === 'deliver') setStage('final')
        }
      }
    } catch (err) {
      setError(`Workflow step failed: ${step}`)
    } finally {
      setLoading(false)
    }
  }

  const workflowData = project || {
    discover: {},
    position: {},
    shape: {},
    visual: {},
    challenge: {},
    consistency: {},
    launch: {},
    final_brand: {}
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">NEXIRA</p>
          <h1>AI Brand Workflow</h1>
        </div>
        <div className="badge">{projectId || 'Draft'}</div>
      </header>

      <main className="layout">
        <section className="panel hero-panel">
          <p className="eyebrow">From raw idea</p>
          <h2>to launch-ready brand.</h2>
          <div className="entry-form">
            <label>
              Project / Product Idea
              <textarea
                value={form.description}
                onChange={(e) => updateField('description', e.target.value)}
                rows="6"
              />
            </label>
            <div className="row">
              <label>
                Target Audience
                <input value={form.audience} onChange={(e) => updateField('audience', e.target.value)} />
              </label>
              <label>
                Industry
                <input value={form.industry} onChange={(e) => updateField('industry', e.target.value)} />
              </label>
            </div>
            <button className="primary" onClick={createProject} disabled={loading}>
              {loading ? 'Building...' : 'Build My Brand'}
            </button>
            {error && <p className="error">{error}</p>}
          </div>
        </section>

        <aside className="panel steps-panel">
          <h3>Workflow</h3>
          <ul className="steps">
            {stageSteps.map((step, index) => (
              <li key={step} className={index <= stageSteps.indexOf(stage.replace('final', 'deliver')) ? 'active' : ''}>
                {index + 1}. {step}
              </li>
            ))}
          </ul>
          <button className="secondary" onClick={() => runWorkflow('discover')}>Run workflow</button>
        </aside>
      </main>

      <section className="results-grid">
        <div className="panel">
          <h3>DISCOVER</h3>
          <p><strong>Core problem:</strong> {workflowData.discover.core_problem || '—'}</p>
          <p><strong>Target users:</strong> {(workflowData.discover.target_users || []).join(', ') || '—'}</p>
          <p><strong>User needs:</strong> {(workflowData.discover.user_needs || []).join(', ') || '—'}</p>
          <p><strong>Open questions:</strong> {(workflowData.discover.open_questions || []).join(', ') || '—'}</p>
        </div>

        <div className="panel">
          <h3>POSITION</h3>
          <p><strong>Category:</strong> {workflowData.position.category || '—'}</p>
          <p><strong>Value proposition:</strong> {workflowData.position.value_proposition || '—'}</p>
          <p><strong>Differentiator:</strong> {workflowData.position.differentiator || '—'}</p>
          <p><strong>Positioning statement:</strong> {workflowData.position.positioning_statement || '—'}</p>
        </div>

        <div className="panel">
          <h3>SHAPE</h3>
          <p><strong>Personality:</strong> {(workflowData.shape.personality || []).map((item) => item.trait).join(', ') || '—'}</p>
          <p><strong>Avoid:</strong> {(workflowData.shape.avoid || []).join(', ') || '—'}</p>
          <p><strong>Territories:</strong> {(workflowData.shape.naming_territories || []).map((t) => t.territory).join(' • ') || '—'}</p>
        </div>

        <div className="panel">
          <h3>VISUAL DIRECTION</h3>
          <p><strong>Color mood:</strong> {(workflowData.visual.color_mood || []).join(', ') || '—'}</p>
          <p><strong>Typography:</strong> {workflowData.visual.typography || '—'}</p>
          <p><strong>Composition:</strong> {workflowData.visual.composition || '—'}</p>
        </div>

        <div className="panel">
          <h3>AI CHALLENGE</h3>
          {(workflowData.challenge.issues || []).map((issue, index) => (
            <div key={index} className="issue-box">
              <strong>{issue.type}</strong> ({issue.severity})
              <p>{issue.description}</p>
              <small>Alternative: {issue.alternative}</small>
            </div>
          )) || '—'}
        </div>

        <div className="panel final-panel">
          <h3>NEXIRA — FINAL BRAND KIT</h3>
          <h4>{workflowData.final_brand.brand_name || 'NEXIRA'}</h4>
          <p className="tagline">{workflowData.final_brand.tagline || workflowData.launch.one_line_pitch || 'From raw idea to launch-ready brand.'}</p>
          <p><strong>Audience:</strong> {workflowData.final_brand.audience || form.audience}</p>
          <p><strong>Problem:</strong> {workflowData.final_brand.problem || workflowData.discover.core_problem || '—'}</p>
          <p><strong>Launch message:</strong> {workflowData.launch.launch_message || '—'}</p>
        </div>
      </section>
    </div>
  )
}

export default App
