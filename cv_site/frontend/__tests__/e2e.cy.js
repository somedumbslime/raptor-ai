// Пример e2e-теста для Cypress
// Запуск: npx cypress open

describe('DragDropBox E2E', () => {
    it('uploads file and shows result', () => {
        cy.visit('/');
        cy.get('input[type="file"]').attachFile('test.jpg');
        cy.contains('loading').should('exist');
        cy.contains('result').should('exist');
    });
    it('shows error for too many files', () => {
        cy.visit('/');
        for (let i = 0; i < 6; i++) {
            cy.get('input[type="file"]').attachFile('test.jpg');
        }
        cy.contains('Maximum').should('exist');
    });
}); 