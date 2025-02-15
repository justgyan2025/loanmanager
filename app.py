from flask import Flask, render_template, request, redirect, url_for, flash, send_file, abort, jsonify, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Admin, Borrower, Loan, Payment
import pandas as pd
import io
from urllib.parse import urljoin
import secrets
from datetime import datetime
import csv
from io import StringIO
import logging
from logging.handlers import RotatingFileHandler
import os

app = Flask(__name__)
app.config.from_object('config.Config')

# Configure logging
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/loan_manager.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Loan Manager startup')

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Admin, int(user_id))

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Admin.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get all loans
    loans = Loan.query.all()
    
    # Calculate summary statistics
    total_loans = len(loans)
    total_amount = sum(loan.amount for loan in loans)
    active_loans = sum(1 for loan in loans if loan.status == 'ACTIVE')
    completed_loans = sum(1 for loan in loans if loan.status == 'COMPLETED')
    
    # Get total borrowers
    total_borrowers = Borrower.query.count()
    
    # Calculate EMI totals
    total_emi_amount = sum(loan.monthly_emi * loan.term_months for loan in loans if loan.monthly_emi)
    total_paid_amount = sum(
        payment.amount 
        for loan in loans 
        for payment in loan.payments
    )
    
    return render_template('dashboard.html',
                         total_loans=total_loans,
                         total_amount=total_amount,
                         active_loans=active_loans,
                         completed_loans=completed_loans,
                         total_borrowers=total_borrowers,
                         total_emi_amount=total_emi_amount,
                         total_paid_amount=total_paid_amount,
                         loans=loans)

@app.route('/borrowers')
@login_required
def borrowers():
    borrowers = Borrower.query.all()
    return render_template('borrowers.html', borrowers=borrowers)

@app.route('/loans')
@login_required
def loans():
    loans = Loan.query.all()
    return render_template('loans.html', loans=loans)

@app.route('/borrower/<int:borrower_id>')
@login_required
def borrower_details(borrower_id):
    borrower = db.session.get(Borrower, borrower_id)
    if borrower is None:
        abort(404)
    return render_template('borrower_details.html', borrower=borrower)

@app.route('/export_borrower_loans/<int:borrower_id>')
@login_required
def export_borrower_loans(borrower_id):
    borrower = db.session.get(Borrower, borrower_id)
    if borrower is None:
        abort(404)
    
    # Create DataFrame from loan data
    loans_data = []
    for loan in borrower.loans:
        for payment in loan.payments:
            loans_data.append({
                'Loan ID': loan.id,
                'Amount': loan.amount,
                'Interest Rate': loan.interest_rate,
                'Status': loan.status,
                'Payment Date': payment.payment_date,
                'Payment Amount': payment.amount
            })
    
    df = pd.DataFrame(loans_data)
    
    # Create CSV file in memory
    output = io.StringIO()
    df.to_csv(output, index=False)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'borrower_{borrower_id}_loans.csv'
    )

@app.route('/borrowers/add', methods=['GET', 'POST'])
@login_required
def add_borrower():
    if request.method == 'POST':
        try:
            # Get form data and strip whitespace
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            address = request.form.get('address', '').strip()
            
            # Validate required fields
            if not first_name or not last_name:
                raise ValueError("First name and last name are required")
            
            # Create new borrower
            new_borrower = Borrower(
                first_name=first_name,
                last_name=last_name,
                address=address if address else None
            )
            
            db.session.add(new_borrower)
            db.session.commit()
            
            flash('Borrower added successfully!', 'success')
            return redirect(url_for('borrowers'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Error adding borrower: {str(e)}")
            flash('An error occurred while adding the borrower. Please try again.', 'error')
            return render_template('add_borrower.html')
    
    return render_template('add_borrower.html')

@app.route('/borrower/<int:borrower_id>/add_loan', methods=['GET', 'POST'])
def add_loan(borrower_id):
    borrower = None
    borrowers = []
    
    if borrower_id == 0:
        # If borrower_id is 0, we're adding a loan from the loans page
        borrowers = Borrower.query.all()
    else:
        # If borrower_id is specified, we're adding a loan for a specific borrower
        borrower = db.session.get(Borrower, borrower_id)
        if borrower is None:
            abort(404)
    
    if request.method == 'POST':
        selected_borrower_id = request.form.get('borrower_id', borrower_id)
        new_loan = Loan(
            borrower_id=selected_borrower_id,
            amount=float(request.form.get('amount')),
            interest_rate=float(request.form.get('interest_rate')),
            term_months=int(request.form.get('term_months')),
            monthly_emi=float(request.form.get('monthly_emi') or 0),
            status=request.form.get('status')
        )
        try:
            db.session.add(new_loan)
            db.session.commit()
            flash('Loan created successfully!', 'success')
            return redirect(url_for('borrower_details', borrower_id=selected_borrower_id))
        except Exception as e:
            db.session.rollback()
            flash('Error creating loan. Please try again.', 'error')
            return render_template('add_loan.html', borrower=borrower, borrowers=borrowers)
    
    return render_template('add_loan.html', borrower=borrower, borrowers=borrowers)

@app.route('/borrower/<int:borrower_id>/edit', methods=['GET', 'POST'])
def edit_borrower(borrower_id):
    borrower = db.session.get(Borrower, borrower_id)
    if not borrower:
        abort(404)
    
    if request.method == 'POST':
        try:
            borrower.first_name = request.form.get('first_name')
            borrower.last_name = request.form.get('last_name')
            borrower.address = request.form.get('address')
            
            db.session.commit()
            flash('Borrower updated successfully!', 'success')
            return redirect(url_for('borrower_details', borrower_id=borrower.id))
        except Exception as e:
            db.session.rollback()
            flash('Error updating borrower. Please try again.', 'error')
    
    return render_template('edit_borrower.html', borrower=borrower)

@app.route('/loan/<int:loan_id>/edit', methods=['GET', 'POST'])
def edit_loan(loan_id):
    loan = db.session.get(Loan, loan_id)
    if loan is None:
        abort(404)
    
    if request.method == 'POST':
        try:
            loan.amount = float(request.form.get('amount'))
            loan.interest_rate = float(request.form.get('interest_rate'))
            loan.term_months = int(request.form.get('term_months'))
            loan.monthly_emi = float(request.form.get('monthly_emi') or 0)
            loan.status = request.form.get('status')
            
            db.session.commit()
            flash('Loan updated successfully!', 'success')
            return redirect(url_for('borrower_details', borrower_id=loan.borrower_id))
        except Exception as e:
            db.session.rollback()
            flash('Error updating loan. Please try again.', 'error')
            return render_template('edit_loan.html', loan=loan)
    
    return render_template('edit_loan.html', loan=loan)

@app.route('/borrower/<int:borrower_id>/delete', methods=['POST'])
@login_required
def delete_borrower(borrower_id):
    borrower = db.session.get(Borrower, borrower_id)
    if borrower is None:
        abort(404)
    
    try:
        # Get the number of loans before deletion for better error message
        num_loans = len(borrower.loans)
        
        db.session.delete(borrower)
        db.session.commit()
        flash(f'Borrower and their {num_loans} loan(s) deleted successfully!', 'success')
        return redirect(url_for('borrowers'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting borrower: {str(e)}. Please try again.', 'error')
        return redirect(url_for('borrower_details', borrower_id=borrower_id))

@login_required
@app.route('/loan/<int:loan_id>/delete', methods=['POST'])
def delete_loan(loan_id):
    loan = db.session.get(Loan, loan_id)
    if loan is None:
        abort(404)
    
    borrower_id = loan.borrower_id
    try:
        # Get the loan amount for better feedback
        loan_amount = loan.amount
        db.session.delete(loan)
        db.session.commit()
        flash(f'Loan #{loan.id} (${loan_amount:,.2f}) deleted successfully!', 'success')
        return redirect(url_for('borrower_details', borrower_id=borrower_id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting loan: {str(e)}. Please try again.', 'error')
        return redirect(url_for('borrower_details', borrower_id=borrower_id))

@app.route('/loan/<int:loan_id>/payments')
@login_required
def payment_history(loan_id):
    loan = db.session.get(Loan, loan_id)
    if loan is None:
        abort(404)
    
    payments = Payment.query.filter_by(loan_id=loan_id).order_by(Payment.payment_date.desc()).all()
    
    # Calculate payment summaries
    principal_paid = sum(p.amount for p in payments if p.payment_type == 'PRINCIPAL')
    interest_paid = sum(p.amount for p in payments if p.payment_type == 'INTEREST')
    penalty_paid = sum(p.amount for p in payments if p.payment_type == 'PENALTY')
    remaining_principal = loan.amount - principal_paid
    total_paid = principal_paid + interest_paid + penalty_paid
    
    return render_template('payment_history.html', 
                         loan=loan, 
                         payments=payments,
                         principal_paid=principal_paid,
                         interest_paid=interest_paid,
                         penalty_paid=penalty_paid,
                         total_paid=total_paid,
                         remaining_principal=remaining_principal,
                         today_date=datetime.now().strftime('%Y-%m-%d'))

@app.route('/loan/<int:loan_id>/make_payment', methods=['GET', 'POST'])
@login_required
def make_payment(loan_id):
    loan = db.session.get(Loan, loan_id)
    if loan is None:
        abort(404)
    
    if request.method == 'POST':
        try:
            # Get payment amounts
            principal_amount = float(request.form.get('principal_amount') or 0)
            interest_amount = float(request.form.get('interest_amount') or 0)
            penalty_amount = float(request.form.get('penalty_amount') or 0)
            
            # Validate at least one payment is made
            if principal_amount <= 0 and interest_amount <= 0 and penalty_amount <= 0:
                raise ValueError("At least one payment amount must be greater than zero")
            
            payment_date = datetime.strptime(request.form.get('payment_date'), '%Y-%m-%d')
            
            # Validate payment date
            if payment_date > datetime.now():
                raise ValueError("Payment date cannot be in the future")
            
            notes = request.form.get('notes')
            
            # Create payments for each non-zero amount
            if principal_amount > 0:
                principal_payment = Payment(
                    loan_id=loan_id,
                    amount=principal_amount,
                    payment_type='PRINCIPAL',
                    payment_date=payment_date,
                    notes=notes,
                    status='COMPLETED'
                )
                db.session.add(principal_payment)
            
            if interest_amount > 0:
                interest_payment = Payment(
                    loan_id=loan_id,
                    amount=interest_amount,
                    payment_type='INTEREST',
                    payment_date=payment_date,
                    notes=notes,
                    status='COMPLETED'
                )
                db.session.add(interest_payment)
            
            if penalty_amount > 0:
                penalty_payment = Payment(
                    loan_id=loan_id,
                    amount=penalty_amount,
                    payment_type='PENALTY',
                    payment_date=payment_date,
                    notes=notes,
                    status='COMPLETED'
                )
                db.session.add(penalty_payment)
            
            # Update loan status
            total_principal_paid = sum(p.amount for p in loan.payments if p.payment_type == 'PRINCIPAL') + principal_amount
            if total_principal_paid >= loan.amount:
                loan.status = 'COMPLETED'
            elif loan.status == 'PENDING':
                loan.status = 'ACTIVE'
            
            db.session.commit()
            total_paid = principal_amount + interest_amount + penalty_amount
            flash(f'Payment of ₹{total_paid:.2f} recorded successfully!', 'success')
            return redirect(url_for('payment_history', loan_id=loan_id))
        except ValueError as e:
            db.session.rollback()
            flash(str(e), 'error')
            return render_template('make_payment.html', loan=loan, today=datetime.now().strftime('%Y-%m-%d'))
        except Exception as e:
            db.session.rollback()
            print(f"Error recording payment: {str(e)}")  # Debug print
            flash('Error recording payment. Please try again.', 'error')
            return render_template('make_payment.html', loan=loan, today=datetime.now().strftime('%Y-%m-%d'))
    
    return render_template('make_payment.html', loan=loan, today=datetime.now().strftime('%Y-%m-%d'))

@app.route('/loan/<int:loan_id>/view/<string:share_token>')
def public_loan_view(loan_id, share_token):
    loan = db.session.get(Loan, loan_id)
    if loan is None:
        abort(404)
    
    # Check if this share token matches any loan of this borrower
    borrower_loans = Loan.query.filter_by(borrower_id=loan.borrower_id).all()
    valid_tokens = [l.share_token for l in borrower_loans]
    
    if share_token not in valid_tokens:
        abort(404)
    
    return render_template('public_loan_view.html', loan=loan)

@app.route('/loan/<int:loan_id>/share', methods=['POST'])
@login_required
def generate_share_link(loan_id):
    loan = db.session.get(Loan, loan_id)
    if loan is None:
        abort(404)
    
    # Generate a unique token if not exists
    if not loan.share_token:
        loan.share_token = secrets.token_urlsafe(16)
        db.session.commit()
    
    # Generate the full URL
    share_url = urljoin(request.host_url, 
                       url_for('public_borrower_view', 
                              borrower_id=loan.borrower_id, 
                              share_token=loan.share_token))
    
    return jsonify({'share_url': share_url})

@app.route('/borrower/<int:borrower_id>/view/<string:share_token>')
def public_borrower_view(borrower_id, share_token):
    borrower = db.session.get(Borrower, borrower_id)
    if borrower is None:
        abort(404)
    
    # Check if this share token matches any loan of this borrower
    valid_tokens = [l.share_token for l in borrower.loans]
    if share_token not in valid_tokens:
        abort(404)
    
    # Calculate payment summaries for each loan
    loan_summaries = []
    for loan in borrower.loans:
        principal_paid = sum(p.amount for p in loan.payments if p.payment_type == 'PRINCIPAL')
        interest_paid = sum(p.amount for p in loan.payments if p.payment_type == 'INTEREST')
        penalty_paid = sum(p.amount for p in loan.payments if p.payment_type == 'PENALTY')
        total_paid = principal_paid + interest_paid + penalty_paid
        
        loan_summaries.append({
            'loan': loan,
            'principal_paid': principal_paid,
            'interest_paid': interest_paid,
            'penalty_paid': penalty_paid,
            'total_paid': total_paid
        })
    
    return render_template('public_borrower_view.html', 
                         borrower=borrower, 
                         loan_summaries=loan_summaries,
                         share_token=share_token)

def format_indian_currency(amount):
    """Format amount in Indian currency style (e.g., Rs. 1,00,000.00)"""
    try:
        # Convert to string with 2 decimal places
        str_amount = f"{float(amount):.2f}"
        # Split into whole and decimal parts
        whole, decimal = str_amount.split('.')
        # Convert to integer for easier manipulation
        whole = int(whole)
        # Format whole number part with Indian style commas
        if whole >= 1000:
            s = str(whole)
            # Place first comma after 3 digits from right
            result = s[-3:]
            s = s[:-3]
            # Then place commas after every 2 digits
            while s:
                result = s[-2:] + ',' + result if s[-2:] else s[-1] + ',' + result
                s = s[:-2]
            whole = result
        return f"Rs. {whole}.{decimal}"
    except (ValueError, TypeError):
        return "Rs. 0.00"

@app.route('/borrower/<int:borrower_id>/loans/export/<string:share_token>')
def export_borrower_loans_csv(borrower_id, share_token):
    borrower = db.session.get(Borrower, borrower_id)
    if not borrower:
        abort(404)
        
    # Verify share token
    valid_tokens = [l.share_token for l in borrower.loans]
    if share_token not in valid_tokens:
        abort(404)

    # Create CSV data
    si = StringIO()
    cw = csv.writer(si)
    
    # Write Borrower Information
    cw.writerow(['BORROWER INFORMATION'])
    cw.writerow(['Name', f"{borrower.first_name} {borrower.last_name}"])
    cw.writerow(['Address', borrower.address or 'Not provided'])
    cw.writerow([])  # Empty row for spacing
    
    for loan in borrower.loans:
        # Calculate payment summaries
        principal_paid = sum(p.amount for p in loan.payments if p.payment_type == 'PRINCIPAL')
        interest_paid = sum(p.amount for p in loan.payments if p.payment_type == 'INTEREST')
        penalty_paid = sum(p.amount for p in loan.payments if p.payment_type == 'PENALTY')
        total_paid = principal_paid + interest_paid + penalty_paid
        
        # Write Loan Details
        cw.writerow(['LOAN DETAILS - ID #' + str(loan.id)])
        cw.writerow(['Amount', format_indian_currency(loan.amount)])
        cw.writerow(['Interest Rate', f"{loan.interest_rate:.1f}%"])
        cw.writerow(['Term', f"{loan.term_months} months"])
        cw.writerow(['Monthly EMI', format_indian_currency(loan.monthly_emi) if loan.monthly_emi else 'N/A'])
        cw.writerow(['Status', loan.status])
        cw.writerow(['Created Date', loan.created_at.strftime('%Y-%m-%d')])
        cw.writerow([])
        
        # Write Payment Summary
        cw.writerow(['PAYMENT SUMMARY'])
        cw.writerow(['Principal Paid', format_indian_currency(principal_paid)])
        cw.writerow(['Interest Paid', format_indian_currency(interest_paid)])
        cw.writerow(['Penalty Paid', format_indian_currency(penalty_paid)])
        cw.writerow(['Total Paid', format_indian_currency(total_paid)])
        cw.writerow([])
        
        # Write Payment History
        cw.writerow(['PAYMENT HISTORY'])
        cw.writerow(['Date', 'Amount', 'Type', 'Status', 'Notes'])
        for payment in loan.payments:
            cw.writerow([
                payment.payment_date.strftime('%Y-%m-%d'),
                format_indian_currency(payment.amount),
                payment.payment_type,
                payment.status,
                payment.notes or '-'
            ])
        cw.writerow([])  # Empty row between loans
        cw.writerow([])  # Double spacing between loans
    
    # Create the response
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=loan_report_{borrower.last_name}_{datetime.now().strftime('%Y%m%d')}.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route('/loan/<int:loan_id>/payments/export')
@login_required
def export_loan_payments_csv(loan_id):
    loan = db.session.get(Loan, loan_id)
    if not loan:
        abort(404)

    # Create CSV data
    si = StringIO()
    cw = csv.writer(si)
    
    # Write headers
    cw.writerow(['Payment Date', 'Amount', 'Type', 'Status', 'Notes'])
    
    # Write payment data
    for payment in loan.payments:
        cw.writerow([
            payment.payment_date.strftime('%Y-%m-%d'),
            format_indian_currency(payment.amount),
            payment.payment_type,
            payment.status,
            payment.notes or ''
        ])
    
    # Create the response
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=loan_{loan_id}_payments_{datetime.now().strftime('%Y%m%d')}.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route('/borrower/<int:borrower_id>/export')
@login_required
def export_borrower_details_csv(borrower_id):
    borrower = db.session.get(Borrower, borrower_id)
    if not borrower:
        abort(404)

    # Create CSV data
    si = StringIO()
    cw = csv.writer(si)
    
    # Write borrower details
    cw.writerow(['Borrower Details'])
    cw.writerow(['Name', f"{borrower.first_name} {borrower.last_name}"])
    cw.writerow(['Address', borrower.address or 'Not provided'])
    cw.writerow([])  # Empty row for spacing
    
    # Write loan summary
    cw.writerow(['Loans Summary'])
    cw.writerow(['Loan ID', 'Amount', 'Interest Rate', 'Term', 'Status', 'EMI'])
    for loan in borrower.loans:
        cw.writerow([
            loan.id,
            format_indian_currency(loan.amount),
            f"{loan.interest_rate:.1f}%",
            f"{loan.term_months} months",
            loan.status,
            format_indian_currency(loan.monthly_emi) if loan.monthly_emi else 'N/A'
        ])
    
    # Create the response
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=borrower_{borrower.last_name}_{datetime.now().strftime('%Y%m%d')}.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route('/loans/export')
@login_required
def export_all_loans_csv():
    # Get all loans with borrower information
    loans = Loan.query.all()
    
    # Create CSV data
    si = StringIO()
    cw = csv.writer(si)
    
    # Write headers
    cw.writerow(['LOAN DETAILS'])
    cw.writerow(['Loan ID', 'Borrower Name', 'Amount', 'Interest Rate', 'Term', 'Monthly EMI', 'Status', 'Created Date'])
    
    # Write loan data
    for loan in loans:
        # Calculate payment summaries
        principal_paid = sum(p.amount for p in loan.payments if p.payment_type == 'PRINCIPAL')
        interest_paid = sum(p.amount for p in loan.payments if p.payment_type == 'INTEREST')
        penalty_paid = sum(p.amount for p in loan.payments if p.payment_type == 'PENALTY')
        total_paid = principal_paid + interest_paid + penalty_paid
        
        cw.writerow([
            loan.id,
            f"{loan.borrower.first_name} {loan.borrower.last_name}",
            format_indian_currency(loan.amount),
            f"{loan.interest_rate:.1f}%",
            f"{loan.term_months} months",
            format_indian_currency(loan.monthly_emi) if loan.monthly_emi else 'N/A',
            loan.status,
            loan.created_at.strftime('%Y-%m-%d')
        ])
        
        # Add payment summary
        cw.writerow([])
        cw.writerow(['Payment Summary'])
        cw.writerow(['Principal Paid', format_indian_currency(principal_paid)])
        cw.writerow(['Interest Paid', format_indian_currency(interest_paid)])
        cw.writerow(['Penalty Paid', format_indian_currency(penalty_paid)])
        cw.writerow(['Total Paid', format_indian_currency(total_paid)])
        cw.writerow([])
        
        # Add payment history
        cw.writerow(['Payment History'])
        cw.writerow(['Date', 'Amount', 'Type', 'Status', 'Notes'])
        for payment in loan.payments:
            cw.writerow([
                payment.payment_date.strftime('%Y-%m-%d'),
                format_indian_currency(payment.amount),
                payment.payment_type,
                payment.status,
                payment.notes or '-'
            ])
        cw.writerow([])  # Empty row between loans
        cw.writerow([])  # Double spacing between loans
    
    # Create response
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename=all_loans_{datetime.now().strftime('%Y%m%d')}.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    app.logger.error(f'Server Error: {error}')
    return render_template('error.html', error=error), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error=error), 404

@app.before_request
def before_request():
    try:
        db.session.ping()
    except Exception:
        db.session.rollback()

if __name__ == '__main__':
    app.run(debug=True) 