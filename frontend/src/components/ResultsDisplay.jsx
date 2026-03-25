function ResultsDisplay({ data }) {
  if (!data || !data.data || data.data.length === 0) {
    return (
      <div className="results">
        <h2>Extraction Results</h2>
        <p className="no-data">No data was extracted from the document.</p>
      </div>
    )
  }

  const columns = Object.keys(data.data[0])

  return (
    <div className="results">
      <h2>Extraction Results</h2>
      <p className="row-count">
        <strong>Rows extracted:</strong> {data.row_count}
      </p>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              {columns.map((col) => (
                <th key={col}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.data.map((row, idx) => (
              <tr key={idx}>
                {columns.map((col) => (
                  <td key={`${idx}-${col}`}>{row[col]}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default ResultsDisplay